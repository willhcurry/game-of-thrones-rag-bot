import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const body = await request.json();
  const question = (body.text || '').toLowerCase();
  
  let response = '';
  
  // Simple keyword-based responses
  if (question.includes('ned stark')) {
    response = "Eddard \"Ned\" Stark was the Lord of Winterfell and Warden of the North. Born to House Stark, he was known for his unwavering honor and sense of duty. He served as Hand of the King to his friend Robert Baratheon, but was ultimately executed under false charges of treason by King Joffrey Baratheon.";
  } 
  else if (question.includes('tyrion')) {
    response = "Tyrion Lannister is the youngest child of Tywin Lannister. Despite being born a dwarf and facing prejudice, he possesses a keen intellect and cunning mind. Known for his wit and diplomatic skills, he served as Hand of the King to both Joffrey Baratheon and later to Daenerys Targaryen. His complicated relationship with his family is a central storyline in the books.";
  }
  else if (question.includes('lannister')) {
    response = "House Lannister is one of the Great Houses of Westeros, ruling over the Westerlands from their seat at Casterly Rock. Known for their immense wealth due to gold mines beneath their ancestral home, their house words are \"Hear Me Roar!\" though their unofficial motto \"A Lannister always pays his debts\" is more widely known. Key members include Tywin, Cersei, Jaime, and Tyrion Lannister.";
  }
  else if (question.includes('stark')) {
    response = "House Stark is the principal noble house of the North. Their seat is Winterfell, one of the oldest castles in the Seven Kingdoms. Known for their honor and hardiness, the Starks have ruled the North for thousands of years. Their house words are \"Winter is Coming,\" a reminder to always be prepared for hardship. Major members include Eddard (Ned), Catelyn, Robb, Sansa, Arya, Bran, and Rickon Stark.";
  }
  else if (question.includes('targaryen')) {
    response = "House Targaryen is a noble family of Valyrian descent who once ruled the Seven Kingdoms of Westeros. Known for their distinctive silver hair, purple eyes, and ability to bond with dragons, they conquered Westeros under Aegon the Conqueror. Their house words are \"Fire and Blood.\" Their nearly 300-year dynasty ended with the rebellion that overthrew the Mad King, Aerys II. Daenerys Targaryen is one of the last known Targaryens.";
  }
  else if (question.includes('jon snow')) {
    response = "Jon Snow is the bastard son of Eddard Stark, raised at Winterfell alongside his trueborn siblings. He joined the Night's Watch and rose to become Lord Commander. Skilled with a sword and possessing strong leadership qualities, Jon is known for his honor and sense of duty, traits he inherited from his father. In the later books, mysteries about his true parentage begin to unfold.";
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
