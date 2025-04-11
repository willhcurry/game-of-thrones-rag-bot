import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log("Request to Hugging Face:", body);
    
    // Extract the question from whatever format it comes in
    const question = body.text || (body.data && body.data[0]) || "";
    
    if (!question) {
      return NextResponse.json({
        status: 'error',
        response: "I didn't receive a question. Please try again."
      });
    }
    
    // Make the request to Hugging Face - IMPORTANT: Using the correct format
    const response = await fetch('https://willhcurry-gotbot.hf.space/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        data: [question]  // This is the correct format as shown in the Hugging Face API tab
      })
    });
    
    if (!response.ok) {
      console.error(`Hugging Face API error: ${response.status}`);
      // Try to get more error details
      const errorText = await response.text();
      console.error(`Error details: ${errorText}`);
      throw new Error(`Hugging Face API returned status ${response.status}`);
    }
    
    const data = await response.json();
    console.log("Response from Hugging Face:", data);
    
    // Extract the response text properly
    let answer = "No response received";
    if (data.data && Array.isArray(data.data) && data.data[0]) {
      if (data.data[0].response) {
        answer = data.data[0].response;
      } else if (typeof data.data[0] === 'string') {
        answer = data.data[0];
      } else {
        answer = JSON.stringify(data.data[0]);
      }
    }
    
    return NextResponse.json({
      status: 'success',
      response: answer
    });
  } catch (error) {
    console.error('Error connecting to Hugging Face API:', error);
    return NextResponse.json({
      status: 'error',
      response: "I'm having trouble connecting to my knowledge base."
    }, { status: 502 });
  }
}
