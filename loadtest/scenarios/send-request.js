// Send request: ask someone for a referral (placeholder endpoint until Phase 1).
import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, protocolOptions, writeSummary } from '../lib/protocol.js';

export const options = protocolOptions(10);

export default function () {
  const body = JSON.stringify({
    to_user_id: Math.floor(Math.random() * 1000),
    company_id: Math.floor(Math.random() * 50),
    message: 'Could you refer me?',
  });
  const response = http.post(`${BASE_URL}/referral-requests`, body, {
    headers: { 'Content-Type': 'application/json' },
  });
  check(response, { 'status is 201': (r) => r.status === 201 });
}

export const handleSummary = writeSummary;
