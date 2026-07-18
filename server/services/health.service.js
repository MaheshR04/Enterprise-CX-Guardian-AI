import { AIClient } from '../integrations/aiClient.js';

/**
 * Health Service Manager.
 * Measures Node server status, Python service connectivity, and calculates overall health.
 */
class HealthService {
  /**
   * Compiles comprehensive system health metrics.
   */
  async getSystemHealth() {
    const startTime = Date.now();

    // 1. Check Node Server status
    const nodeStatus = {
      status: 'healthy',
      server: 'Enterprise CX Guardian AI Node Backend',
      version: '1.0.0',
      uptime: `${Math.floor(process.uptime())}s`,
      timestamp: new Date().toISOString()
    };

    // 2. Check Python AI Microservice status & measure response time
    const aiStartTime = Date.now();
    const aiHealthResult = await AIClient.checkHealth();
    const aiResponseTimeMs = Date.now() - aiStartTime;

    const pythonStatus = {
      status: aiHealthResult.status === 'healthy' ? 'healthy' : 'unreachable',
      responseTimeMs: `${aiResponseTimeMs}ms`,
      details: aiHealthResult.data || null,
      error: aiHealthResult.error || null
    };

    // 3. Determine Overall System Health
    let overallStatus = 'healthy';
    if (pythonStatus.status !== 'healthy') {
      overallStatus = 'degraded';
    }

    const totalLatencyMs = Date.now() - startTime;

    return {
      status: overallStatus,
      totalLatencyMs: `${totalLatencyMs}ms`,
      nodeServer: nodeStatus,
      pythonService: pythonStatus
    };
  }
}

const healthServiceInstance = new HealthService();
export default healthServiceInstance;
