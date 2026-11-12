// Search: "who can refer me at company X?" (placeholder endpoint until Phase 1).
import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, protocolOptions, writeSummary } from '../lib/protocol.js';

export const options = protocolOptions(50);

export default function () {
  const company = `Company ${Math.floor(Math.random() * 50)}`;
  const response = http.get(`${BASE_URL}/search?company=${encodeURIComponent(company)}`, {
    tags: { name: 'GET /search' },
  });
  check(response, { 'status is 200': (r) => r.status === 200 });
}

export const handleSummary = writeSummary;
