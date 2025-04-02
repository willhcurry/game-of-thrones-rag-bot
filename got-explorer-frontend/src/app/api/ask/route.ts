import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const question = body.text?.toLowerCase() || '';
    
    // Direct mapping of content based on specific keywords
    let response = '';
    
    if (question.includes('ned stark')) {
      response = "Eddard \"Ned\" Stark was the Lord of Winterfell and Warden of the North. He was known for his honor and integrity. He served as Hand of the King to Robert Baratheon before being executed by Joffrey Baratheon.";
    } 
    else if (question.includes('tyrion')) {
      response = "Tyrion Lannister is the youngest son of Tywin Lannister. He is a dwarf and known for his high intelligence and wit. Despite facing prejudice throughout his life, he served as Hand of the King to Daenerys Targaryen.";
    }
    else if (question.includes('lannister')) {
      response = "House Lannister is one of the Great Houses of the Seven Kingdoms, ruling over the Westerlands from their seat of Casterly Rock. They are known for their wealth and their saying, \"A Lannister always pays his debts.\"";
    }
    else {
      response = "I don't have specific information about that from the Game of Thrones books.";
    }
    
    return NextResponse.json({
      status: 'success',
      response: response
    });
  } catch (error) {
    const errorMessage = error instanceof Error 
      ? error.message 
      : 'An unknown error occurred';
    
    return NextResponse.json(
      { status: 'error', response: errorMessage },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
}
