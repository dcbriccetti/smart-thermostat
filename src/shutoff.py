from time import monotonic

HEAT_REENABLE_AFTER_SECS = 180


class AnticipatoryShutoff:
    def __init__(self, knob, degrees_of_heat_needed):
        self.knob = knob
        self.period_start = monotonic() + self.knob.value_between(30, 60 * 10)
        self.period_end = self.period_start + HEAT_REENABLE_AFTER_SECS if degrees_of_heat_needed < 1 else None

    def beyond_suppression_period(self):
        return monotonic() > self.period_end

    def in_suppression_period(self):
        return self.period_start < monotonic() < self.period_end
