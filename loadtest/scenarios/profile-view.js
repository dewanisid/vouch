// Profile view: open one person's profile (placeholder endpoint until Phase 1).
import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, protocolOptions, writeSummary } from '../lib/protocol.js';

export const options = protocolOptions(50);

export default function () {
  const userId = Math.floor(Math.random() * 1000);
  const response = http.get(`${BASE_URL}/profiles/${userId}`, {
    tags: { name: 'GET /profiles/{id}' },
  });
  check(response, { 'status is 200': (r) => r.status === 200 });
}

export const handleSummary = writeSummary;
