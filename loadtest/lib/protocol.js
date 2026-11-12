// Shared rules from docs/benchmark-protocol.md, so every scenario measures the same way.
//
// Two phases run back to back at the same fixed request rate:
//   warmup  - its numbers are thrown away
//   measure - the numbers we report
// The rate is an arrival rate: k6 starts RATE requests per second whatever the
// server's speed, so a slow server can't make the test go easier on it.

export const BASE_URL = __ENV.BASE_URL || 'http://api:8000';

export function protocolOptions(defaultRate) {
  const rate = Number(__ENV.RATE || defaultRate);
  const warmup = __ENV.WARMUP || '2m';
  const duration = __ENV.DURATION || '5m';

  const load = {
    executor: 'constant-arrival-rate',
    rate,
    timeUnit: '1s',
    preAllocatedVUs: Math.max(10, rate),
    maxVUs: rate * 10,
  };

  return {
    scenarios: {
      warmup: { ...load, duration: warmup, gracefulStop: '0s' },
      measure: { ...load, duration, startTime: warmup },
    },
    summaryTrendStats: ['p(50)', 'p(99)', 'max'],
    // Thresholds that always pass. They exist so the summary reports the
    // measure phase on its own, separate from the warm-up.
    thresholds: {
      'http_req_duration{scenario:measure}': ['max>=0'],
      'http_reqs{scenario:measure}': ['count>=0'],
      'http_req_failed{scenario:measure}': ['rate>=0'],
      'dropped_iterations{scenario:measure}': ['count>=0'],
    },
  };
}

export function writeSummary(data) {
  return { [__ENV.SUMMARY_OUT || 'results/summary.json']: JSON.stringify(data) };
}
