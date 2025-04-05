import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const question = (body.text || '').toLowerCase();
    
    let response = '';
    
    // Enhanced hardcoded responses for common questions
    if (question.includes('jon snow')) {
      response = "Jon Snow is the bastard son of Eddard Stark, raised at Winterfell. He joined the Night's Watch and rose to become Lord Commander. Known for his honor and skill with a sword, Jon is often accompanied by his direwolf, Ghost.";
    } 
    else if (question.includes('red wedding')) {
      response = "The Red Wedding was a massacre orchestrated by Lord Walder Frey, Lord Roose Bolton, and Tywin Lannister. During the wedding feast of Edmure Tully and Roslin Frey at the Twins, the Freys and Boltons betrayed and murdered King Robb Stark, his mother Catelyn, his wife Talisa, and many of their bannermen.";
    }
    else if (question.includes('stark')) {
      response = "House Stark is the principal noble house of the North. Their seat is Winterfell, one of the oldest castles in the Seven Kingdoms. Known for their honor and hardiness, the Starks have ruled the North for thousands of years. Their house words are \"Winter is Coming.\" Major members include Eddard (Ned), Catelyn, Robb, Sansa, Arya, Bran, and Rickon Stark.";
    }
    else if (question.includes('lannister')) {
      response = "House Lannister is one of the Great Houses of Westeros, ruling over the Westerlands from their seat at Casterly Rock. Known for their immense wealth due to gold mines beneath their ancestral home, their house words are \"Hear Me Roar!\" though their unofficial motto \"A Lannister always pays his debts\" is more widely known. Key members include Tywin, Cersei, Jaime, and Tyrion Lannister.";
    }
    else if (question.includes('targaryen')) {
      response = "House Targaryen is a noble family of Valyrian descent who once ruled the Seven Kingdoms of Westeros. Known for their distinctive silver hair, purple eyes, and ability to bond with dragons, they conquered Westeros under Aegon the Conqueror. Their house words are \"Fire and Blood.\" Their nearly 300-year dynasty ended with the rebellion that overthrew the Mad King, Aerys II. Daenerys Targaryen is one of the last known Targaryens.";
    }
    else if (question.includes('dragon')) {
      response = "Dragons in Game of Thrones are fearsome creatures with immense power. Once numerous under Targaryen rule, they were thought extinct until Daenerys Targaryen hatched three dragon eggs: Drogon, Rhaegal, and Viserion. These fire-breathing creatures grow throughout their lives and form strong bonds with their riders, traditionally of Valyrian blood. Dragons played a crucial role in the Targaryen conquest of Westeros.";
    }
    else {
      response = "I don't have specific information about that from the Game of Thrones books. Try asking about major characters like Jon Snow, Ned Stark, or Tyrion Lannister, or about houses such as House Stark, Lannister, or Targaryen.";
    }
    
    return NextResponse.json({
      status: 'success',
      response: response
    });
  } catch (error) {
    console.error('Error in /api/ask:', error);
    return NextResponse.json({
      status: 'error',
      response: "Sorry, I encountered an error processing your question."
    }, { status: 500 });
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
