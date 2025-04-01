export default function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  if (req.method === 'POST') {
    try {
      const question = req.body.text || 'No question received';
      res.status(200).json({
        status: 'success',
        response: `You asked: "${question}". This is a test response from the Vercel API route.`
      });
    } catch (error) {
      res.status(500).json({ status: 'error', response: error.message });
    }
  } else {
    res.status(405).json({ status: 'error', response: 'Method not allowed' });
  }
}
