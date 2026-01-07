// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
const REQUEST_TIMEOUT = 60000; // 60 seconds for complex queries

/**
 * Generate Nmap Command from Natural Language Query
 * @param {string} queryText - The user's natural language query
 * @param {object} context - Optional context information (e.g., {target: "192.168.1.10"})
 * @returns {Promise<object>} - The command generation result
 */
export const generateCommand = async (queryText, context = {}) => {
  // Prepare request payload matching backend schema
  const requestPayload = {
    text: queryText,
  };
  
  
  console.log('📤 Sending to API:', requestPayload);
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    const response = await fetch(`${API_BASE_URL}/command/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestPayload),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    console.log('📥 Response status:', response.status);

    // Handle different error responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('❌ API Error:', errorData);
      
      // Parse backend error messages
      if (response.status === 400) {
        throw new Error(parseBackendError(errorData.detail));
      } else if (response.status === 503) {
        throw new Error('Backend service temporarily unavailable. Some agents may be offline.');
      } else if (response.status === 500) {
        throw new Error('Internal server error. Please try again.');
      } else {
        throw new Error(errorData.detail || `API Error: ${response.statusText}`);
      }
    }

    const data = await response.json();
    console.log('✅ API Response:', data);
    
    return transformBackendResponse(data, queryText);

  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('Request timeout. The query may be too complex or the service is slow.');
    }
    
    console.error('💥 API Error:', error);
    throw error;
  }
};

/**
 * Parse backend error messages to user-friendly format
 */
const parseBackendError = (detail) => {
  if (typeof detail !== 'string') {
    return 'Command generation failed. Please try again.';
  }

  // Check for specific error patterns
  if (detail.includes('Service indisponible')) {
    return 'AI agent service is currently unavailable. Please try a simpler query or try again later.';
  }
  
  if (detail.includes('échec de génération')) {
    return 'Failed to generate command. The AI agents may be offline. Please try again.';
  }

  if (detail.includes('HTTPException')) {
    return 'Backend configuration error. Please contact system administrator.';
  }

  if (detail.includes('connection') || detail.includes('Connection')) {
    return 'Cannot connect to AI generation service. Some features may be unavailable.';
  }

  return detail;
};

/**
 * Transform backend response to match frontend expected format
 * @param {object} backendData - Response from FastAPI backend (FinalDecision model)
 * @param {string} originalQuery - Original user query
 * @returns {object} - Transformed data for frontend
 */
const transformBackendResponse = (backendData, originalQuery = '') => {
  // Backend returns FinalDecision model:
  // {
  //   command: string,
  //   confidence: float,
  //   flags_explanation: Dict[str, str]
  // }
  return {
    query: {
      query: originalQuery,
      user_id: 'user_123'
    },
    candidate: {
      command: backendData.command,
      rationale: generateRationale(backendData),
      source_agent: backendData.source_agent || 'SYSTEM',
  
      complexity_level: backendData.complexity_level || 'MEDIUM'
    },
    result: {
      status: 'validated',
      command: backendData.command,
      valid: true,
      risk_score: calculateRiskScore(backendData),
      risk_level: calculateRiskLevel(backendData),
      issues: backendData.issues || [],
      warnings: backendData.warnings || extractWarnings(backendData),
      recommendation: generateRecommendation(backendData),
      timestamp: new Date().toISOString(),
      confidence: backendData.confidence,
      flags_explanation: backendData.flags_explanation || {}
    }
  };
};

/**
 * Generate rationale from flags explanation
 */
const generateRationale = (data) => {
  if (!data.flags_explanation || Object.keys(data.flags_explanation).length === 0) {
    return `Generated command with ${(data.confidence * 100).toFixed(1)}% confidence`;
  }

  const explanations = Object.entries(data.flags_explanation)
    .map(([flag, explanation]) => `${flag}: ${explanation}`)
    .join(', ');
  
  return `Command generated with confidence ${(data.confidence * 100).toFixed(1)}%. Flags: ${explanations}`;
};

/**
 * Extract warnings from command analysis
 */
const extractWarnings = (data) => {
  const warnings = [];
  const command = data.command.toLowerCase();

  if (command.includes('-d ') || command.includes('decoy')) {
    warnings.push('Decoy scanning detected - may trigger IDS/IPS');
  }
  if (command.includes('-f')) {
    warnings.push('Packet fragmentation enabled');
  }
  if (command.includes('-ss') || command.includes('-sa')) {
    warnings.push('Stealth scanning mode active');
  }
  if (command.includes('--script')) {
    warnings.push('NSE scripts will be executed');
  }
  if (data.confidence < 0.7) {
    warnings.push('Lower confidence score - verify command before execution');
  }

  return warnings;
};

/**
 * Calculate risk score based on command and confidence
 */
const calculateRiskScore = (data) => {
  const command = data.command.toLowerCase();
  let baseScore = 3.0;

  // High-risk flags
  if (command.includes('-d ') || command.includes('decoy')) baseScore += 2.5;
  if (command.includes('-f') || command.includes('fragment')) baseScore += 1.5;
  if (command.includes('-ss') || command.includes('-sa')) baseScore += 2.0;
  if (command.includes('-o') || command.includes('os')) baseScore += 1.0;
  if (command.includes('--script')) baseScore += 1.5;
  if (command.includes('-a')) baseScore += 2.0;
  if (command.includes('-pn')) baseScore += 1.0;
  if (command.includes('-t4') || command.includes('-t5')) baseScore += 0.5;
  
  // Adjust by confidence (lower confidence = higher risk)
  const confidenceFactor = 1.0 - (data.confidence * 0.3);
  
  return Math.min(10, baseScore * confidenceFactor);
};

/**
 * Calculate risk level based on risk score
 */
const calculateRiskLevel = (data) => {
  const score = calculateRiskScore(data);
  if (score < 4) return 'LOW';
  if (score < 7) return 'MEDIUM';
  return 'HIGH';
};

/**
 * Generate recommendation based on confidence and command
 */
const generateRecommendation = (data) => {
  const riskLevel = calculateRiskLevel(data);
  
  if (data.confidence > 0.8 && riskLevel === 'LOW') {
    return 'Command is valid and ready for execution with high confidence.';
  } else if (data.confidence > 0.7 && riskLevel === 'MEDIUM') {
    return 'Command is valid but review flags before execution. Medium risk detected.';
  } else if (data.confidence > 0.6) {
    return 'Command generated with moderate confidence. Verify flags and target before execution.';
  } else if (riskLevel === 'HIGH') {
    return `High-risk command detected (${riskLevel}). Ensure proper authorization and review all flags carefully.`;
  } else {
    return 'Command generated with lower confidence. Thoroughly review and test in safe environment first.';
  }
};

/**
 * Health check endpoint
 */
export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/health`, {
      method: 'GET',
    });
    return response.ok;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
};

/**
 * Check backend status and available services
 */
export const checkServiceStatus = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/status`, {
      method: 'GET',
    });
    if (response.ok) {
      return await response.json();
    }
    return { available: false, message: 'Status endpoint not available' };
  } catch (error) {
    console.error('Service status check failed:', error);
    return { available: false, message: error.message };
  }
};