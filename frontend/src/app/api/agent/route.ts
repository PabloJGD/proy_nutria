// src/app/api/agent/route.ts
import type { NextRequest } from 'next/server';

const backendUrl = () => {
  const url = process.env.BACKEND_URL;
  if (!url) throw new Error('BACKEND_URL no configurada');
  return url;
};

// Texto sin imagen
export async function GET(request: NextRequest) {
  try {
    const url = `${backendUrl()}/agent?` + new URL(request.url).searchParams.toString();
    const apiRes = await fetch(url);
    const text = await apiRes.text();
    return new Response(text, {
      status: apiRes.status,
      headers: { 'Content-Type': 'text/plain' },
    });
  } catch (e) {
    return new Response(`Error: ${e}`, { status: 500 });
  }
}

// Con imagen
export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const apiRes = await fetch(`${backendUrl()}/agent`, {
      method: 'POST',
      body: formData,
    });
    const text = await apiRes.text();
    return new Response(text, {
      status: apiRes.status,
      headers: { 'Content-Type': 'text/plain' },
    });
  } catch (e) {
    return new Response(`Error: ${e}`, { status: 500 });
  }
}
