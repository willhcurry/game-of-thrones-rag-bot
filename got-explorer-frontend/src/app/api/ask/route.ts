import { NextRequest, NextResponse } from 'next/server';

// Game of Thrones data with actual content
const GOT_DATA = {
  'ned stark': 'Eddard "Ned" Stark was the Lord of Winterfell and Warden of the North. He was known for his honor and integrity. He served as Hand of the King to Robert Baratheon before being executed by Joffrey Baratheon.',
  'jon snow': 'Jon Snow is the bastard son of Eddard Stark who joined the Night\'s Watch. He later became Lord Commander and was eventually revealed to be the son of Lyanna Stark and Rhaegar Targaryen.',
  'winterfell': 'Winterfell is the ancestral castle of House Stark and the seat of power in the North. It was built over a natural hot spring, with hot water running through the walls to keep it warm during the harsh northern winters.',
  'targaryen': 'House Targaryen is a noble family of Valyrian descent who once ruled the Seven Kingdoms. They are known for their silver hair, purple eyes, and their ability to bond with dragons.',
  'lannister': 'House Lannister is one of the Great Houses of the Seven Kingdoms, ruling over the Westerlands from their seat of Casterly Rock. They are known for their wealth and their saying, "A Lannister always pays his debts."',
  'tyrion': 'Tyrion Lannister is the youngest son of Tywin Lannister. He is a dwarf and known for his high intelligence and wit. Despite facing prejudice throughout his life, he served as Hand of the King to Daenerys Targaryen.',
  'casterly rock': 'Casterly Rock is the ancestral seat of House Lannister. The fortress is carved out of a great stone hill and is one of the strongest castles in the Seven Kingdoms. Beneath it are gold mines that made the Lannisters the richest family in Westeros.',
  'tywin': 'Tywin Lannister was the head of House Lannister, Lord of Casterly Rock, and Warden of the West. He was known for his strategic mind, ruthlessness, and his dedication to family legacy.'
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
    let house = "";
    if (question.includes('stark')) house = "House Stark Knowledge";
    else if (question.includes('lannister') || question.includes('tyrion') || question.includes('tywin') || question.includes('casterly')) house = "House Lannister Knowledge";
    else if (question.includes('targaryen')) house = "House Targaryen Knowledge";
    
    return NextResponse.json({
      status: 'success',
      response: response,
      house: house
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
