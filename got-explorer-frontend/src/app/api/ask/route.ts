import { NextRequest, NextResponse } from 'next/server';

// Simple mock data for GoT questions
const GOT_DATA = {
  'ned stark': 'Eddard "Ned" Stark was the Lord of Winterfell and Warden of the North. He was known for his honor and integrity. He served as Hand of the King to Robert Baratheon before being executed by Joffrey Baratheon.',
  'jon snow': 'Jon Snow is the bastard son of Eddard Stark who joined the Night\'s Watch. He later became Lord Commander and was eventually revealed to be the son of Lyanna Stark and Rhaegar Targaryen.',
  'winterfell': 'Winterfell is the ancestral castle of House Stark and the seat of power in the North. It was built over a natural hot spring, with hot water running through the walls to keep it warm during the harsh northern winters.',
  'targaryen': 'House Targaryen is a noble family of Valyrian descent who once ruled the Seven Kingdoms. They are known for their silver hair, purple eyes, and their ability to bond with dragons.',
  'lannister': 'House Lannister is one of the Great Houses of the Seven Kingdoms, ruling over the Westerlands from their seat of Casterly Rock. They are known for their wealth and their saying, "A Lannister always pays his debts."',
};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const question = body.text?.toLowerCase() || '';
    
    // Look for relevant keywords in the question
    let response = "I couldn't find specific information about that in the Game of Thrones books.";
    
    for (const [keyword, info] of Object.entries(GOT_DATA)) {
      if (question.includes(keyword)) {
        response = info;
        break;
      }
    }
    
    // Add house styling based on the question
    let houseStyle = "";
    if (question.includes('stark')) houseStyle = "House Stark Knowledge";
    else if (question.includes('lannister')) houseStyle = "House Lannister Knowledge";
    else if (question.includes('targaryen')) houseStyle = "House Targaryen Knowledge";
    
    return NextResponse.json({
      status: 'success',
      response: response,
      house: houseStyle
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
