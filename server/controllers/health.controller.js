export function getHealth(_req, res) {
  res.status(200).json({
    status: 'ok',
    message: 'GuardianPath API is online',
    timestamp: new Date().toISOString(),
  });
}
