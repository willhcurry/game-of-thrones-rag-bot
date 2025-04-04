import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log("Request to HF:", body);
    
    const response = await fetch('https://willhcurry-gotbot.hf.space/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ data: [body.text || ""] })
    });
    
    const data = await response.json();
    console.log("Response from HF:", data);
    
    // Check for errors in the response
    if (data?.data?.[0]?.error) {
      console.error("Error from Hugging Face:", data.data[0].error);
      return NextResponse.json({
        status: 'success',
        response: "I'm having trouble connecting to my knowledge base. Please try a different question or try again later."
      });
    }
    
    // Extract response or use fallback
    const answer = data?.data?.[0]?.response || 
                   "I couldn't find information about that in the Game of Thrones books.";
    
    return NextResponse.json({
      status: 'success',
      response: answer
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json({
      status: 'success',
      response: "I'm having trouble reaching my knowledge base. Please try again later."
    });
  }
}
