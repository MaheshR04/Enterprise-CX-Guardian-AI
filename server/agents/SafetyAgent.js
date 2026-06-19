import { memoryManager } from './MemoryManager.js';
import { analyzeAllRisks } from './RiskAnalyzer.js';
import { evaluateSafetyState } from './DecisionEngine.js';
import { executeSafetyAction } from './ActionExecutor.js';

class SafetyAgent {
  async onUserUpdate(userId, user, payload) {
    if (!userId || !user) return;

    // 1. Observe: Capture current telemetry and update memory state
    if (payload.location) {
      memoryManager.updateLocation(userId, payload.location);
    }
    if (payload.battery) {
      memoryManager.updateBattery(userId, payload.battery);
    }
    if (payload.activeRoute !== undefined) {
      memoryManager.updateRoute(userId, payload.activeRoute);
    }

    const memory = memoryManager.getMemory(userId);

    // 2. Analyze: Calculate hazard scores from raw variables
    const riskAnalysis = analyzeAllRisks(memory);

    // 3. Reason & Decide: Run threat evaluation rules
    const evaluation = evaluateSafetyState(riskAnalysis);

    // 4. Reflect & Adapt: Check history to throttle repeating alerts
    if (evaluation.actionRequired) {
      const lastAlert = memoryManager.getLastReflection(userId, evaluation.status);
      const THROTTLE_WINDOW_MS = 2 * 60 * 1000; // 2 minutes throttling

      if (lastAlert && (new Date() - new Date(lastAlert.timestamp) < THROTTLE_WINDOW_MS)) {
        // Adapt: Throttling duplicate alert to avoid user alert overload
        return;
      }

      // 5. Act: Fire notifications or escalate to emergency workflows
      await executeSafetyAction(userId, user, evaluation);

      // Record reflection state
      memoryManager.addReflection(userId, evaluation.status, {
        threatScore: evaluation.threatScore,
        reason: evaluation.reason,
      });
    }
  }

  onUserDisconnect(userId) {
    if (userId) {
      memoryManager.clearMemory(userId);
    }
  }
}

export const safetyAgent = new SafetyAgent();
