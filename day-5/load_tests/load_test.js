/**
 * K6 Load Testing Script for Elation Health Chat Bot
 * Run with: k6 run load_tests/load_test.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Define custom metrics
export const errorRate = new Rate('errors');
const apiLatency = new Trend('api_latency');
const apiErrors = new Counter('api_errors');

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp-up
    { duration: '1m30s', target: 50 }, // Stay at 50 VUs
    { duration: '30s', target: 10 },   // Ramp-down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<1000'], // 95th percentile < 1s
    'http_req_failed': ['rate<0.1'],      // Error rate < 10%
  },
};

const BASE_URL = 'http://localhost:8000';

// Test data
const patientContext = {
  patient_id: 'P001',
  name: 'John Doe',
  age: 45,
  gender: 'M',
  conditions: ['Hypertension', 'Type 2 Diabetes'],
  medications: ['Lisinopril 10mg daily', 'Metformin 500mg BID'],
  allergies: ['Penicillin']
};

export default function () {
  group('Health Check', () => {
    const res = http.get(`${BASE_URL}/health`);
    check(res, {
      'health status is 200': (r) => r.status === 200,
      'health response time < 100ms': (r) => r.timings.duration < 100,
    }) || errorRate.add(1);
    apiLatency.add(res.timings.duration);
  });

  sleep(1);

  group('Chat Message', () => {
    const payload = JSON.stringify({
      message: 'Patient presenting with persistent headaches for 2 weeks',
      patient_context: patientContext,
      specialty: 'general_practice'
    });

    const params = {
      headers: { 'Content-Type': 'application/json' },
    };

    const res = http.post(`${BASE_URL}/api/chat/message`, payload, params);
    check(res, {
      'chat status is 200': (r) => r.status === 200,
      'chat response time < 2000ms': (r) => r.timings.duration < 2000,
      'has session_id': (r) => r.json('session_id') !== null,
      'has response': (r) => r.json('response') !== null,
    }) || errorRate.add(1);
    apiLatency.add(res.timings.duration);

    if (res.status !== 200) {
      apiErrors.add(1);
    }
  });

  sleep(2);

  group('Get History', () => {
    // Assume we have a session_id from previous test
    const res = http.get(`${BASE_URL}/api/chat/history/test_session?limit=10`);
    check(res, {
      'history status is 200 or 404': (r) => [200, 404].includes(r.status),
      'history response time < 1000ms': (r) => r.timings.duration < 1000,
    }) || errorRate.add(1);
    apiLatency.add(res.timings.duration);
  });

  sleep(1);

  group('Validate Content', () => {
    const payload = JSON.stringify({
      content: 'Patient has hypertension with BP 150/95. Started on Lisinopril 10mg daily.',
      specialty: 'general_practice'
    });

    const params = {
      headers: { 'Content-Type': 'application/json' },
    };

    const res = http.post(`${BASE_URL}/api/chat/validate`, payload, params);
    check(res, {
      'validate status is 200': (r) => r.status === 200,
      'validate response time < 1500ms': (r) => r.timings.duration < 1500,
      'has is_valid': (r) => r.json('is_valid') !== null,
      'has score': (r) => r.json('score') !== null,
    }) || errorRate.add(1);
    apiLatency.add(res.timings.duration);
  });

  sleep(2);
}

export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'summary.json': JSON.stringify(data),
  };
}

function textSummary(data, options) {
  const indent = options.indent || ' ';
  let summary = '\n📊 Load Test Summary\n';
  summary += '='.repeat(50) + '\n';

  const metrics = data.metrics;
  for (const [name, metric] of Object.entries(metrics)) {
    summary += `${indent}${name}\n`;
    if (metric.values) {
      for (const [key, value] of Object.entries(metric.values)) {
        summary += `${indent}${indent}${key}: ${value}\n`;
      }
    }
  }

  summary += '='.repeat(50) + '\n';
  return summary;
}
