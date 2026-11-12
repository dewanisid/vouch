// Smoke: is the service up and answering under light, steady load?
import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, protocolOptions, writeSummary } from '../lib/protocol.js';

export const options = protocolOptions(20);

export default function () {
  const response = http.get(`${BASE_URL}/health`);
  check(response, { 'status is 200': (r) => r.status === 200 });
}

export const handleSummary = writeSummary;
