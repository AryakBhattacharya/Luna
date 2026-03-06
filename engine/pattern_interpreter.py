class PatternInterpreter:

    @staticmethod
    def interpret(memory):

        insights = []

        avoidance = memory.get("avoidance_patterns", 0)
        directive_follow = memory.get("directive_follow_through", 0)
        insight_accept = memory.get("insight_acceptance", 0)
        conversations = memory.get("conversation_count", 0)

        # Avoidance detection
        if avoidance >= 5:
            insights.append("User tends to hesitate before starting tasks.")

        # Directive responsiveness
        if directive_follow >= 3:
            insights.append("User responds well to clear directives.")

        elif directive_follow == 0 and conversations > 5:
            insights.append("User rarely follows direct instructions.")

        # Insight acceptance
        if insight_accept >= 3:
            insights.append("User is receptive to behavioral observations.")

        # Familiarity level
        if conversations > 10:
            insights.append("User is becoming familiar with Luna.")

        if not insights:
            insights.append("No strong behavioral patterns detected yet.")

        return insights