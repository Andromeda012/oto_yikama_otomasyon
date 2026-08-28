export async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `API request failed: ${response.status}`);
  }

  const contentType = response.headers.get('content-type') || '';
  return contentType.includes('application/json')
    ? response.json()
    : response.text();
}
