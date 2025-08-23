"""
Pronoun Resolution and Personnel Tracking System
Advanced NLP system for identifying key personnel, tracking pronoun references,
and automatically categorizing content with proper source attribution.
"""

import re
import os
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class PersonEntity:
    """Represents a person mentioned in the text"""
    name: str
    full_name: str
    titles: List[str] = field(default_factory=list)
    organizations: List[str] = field(default_factory=list)
    first_mention_position: int = 0
    mention_positions: List[int] = field(default_factory=list)
    pronouns_used: Set[str] = field(default_factory=set)
    credibility_score: float = 0.0
    role_in_article: str = ""
    
@dataclass
class PronounReference:
    """Represents a pronoun and its resolved entity"""
    pronoun: str
    position: int
    sentence: str
    resolved_entity: Optional[PersonEntity] = None
    confidence_score: float = 0.0
    context_window: str = ""

@dataclass
class AttributedStatement:
    """Represents a statement attributed to a specific person"""
    statement: str
    attributed_person: PersonEntity
    statement_type: str  # 'direct_quote', 'paraphrased', 'reported_speech'
    confidence_score: float
    position: int
    context: str
    is_factual_claim: bool = False
    verification_status: str = "unverified"

class PronounResolutionSystem:
    """
    Advanced system for pronoun resolution and personnel tracking in articles.
    Identifies key personnel, tracks pronoun references, and categorizes attributed content.
    """
    
    def __init__(self):
        # Initialize Gemini client
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("No Google API key found. Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.3,  # Lower temperature for more consistent entity recognition
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 4096,
            }
        )
        
        # Pronoun patterns
        self.pronouns = {
            'he', 'him', 'his', 'himself',
            'she', 'her', 'hers', 'herself', 
            'they', 'them', 'their', 'theirs', 'themselves'
        }
        
        # Quote patterns
        self.quote_patterns = [
            r'"([^"]*)"',  # Double quotes
            r"'([^']*)'",  # Single quotes
            r'"([^"]*)"',  # Smart quotes
            r"'([^']*)'",  # Smart single quotes
        ]
        
        # Speech attribution patterns
        self.attribution_patterns = [
            r'(\w+)\s+said',
            r'(\w+)\s+stated',
            r'(\w+)\s+explained',
            r'(\w+)\s+noted',
            r'(\w+)\s+commented',
            r'(\w+)\s+remarked',
            r'(\w+)\s+declared',
            r'(\w+)\s+announced',
            r'(\w+)\s+claimed',
            r'(\w+)\s+argued',
            r'according\s+to\s+(\w+)',
            r'(\w+)\s+told\s+',
            r'(\w+)\s+added',
            r'(\w+)\s+continued'
        ]
        
        # Storage for analysis results
        self.entities: List[PersonEntity] = []
        self.pronoun_references: List[PronounReference] = []
        self.attributed_statements: List[AttributedStatement] = []
        self.text_sentences: List[str] = []
        
    def analyze_text(self, text: str, title: str = "") -> Dict[str, Any]:
        """
        Main analysis function that processes text for pronoun resolution and attribution.
        
        Args:
            text: The article text to analyze
            title: Optional article title for context
            
        Returns:
            Dictionary containing analysis results
        """
        
        # Reset storage
        self.entities = []
        self.pronoun_references = []
        self.attributed_statements = []
        
        # Split text into sentences
        self.text_sentences = self._split_into_sentences(text)
        
        # Step 1: Identify key personnel
        print("🔍 Step 1: Identifying key personnel...")
        self.entities = self._identify_personnel(text, title)
        
        # Step 2: Find and resolve pronoun references
        print("🔗 Step 2: Resolving pronoun references...")
        self.pronoun_references = self._resolve_pronouns(text)
        
        # Step 3: Identify and attribute statements
        print("💬 Step 3: Identifying attributed statements...")
        self.attributed_statements = self._identify_attributed_statements(text)
        
        # Step 4: Classify statement types and verify factual claims
        print("✅ Step 4: Classifying statements and verifying claims...")
        self._classify_and_verify_statements()
        
        # Generate analysis results
        results = self._generate_analysis_results()
        
        print(f"✅ Analysis complete: {len(self.entities)} entities, {len(self.pronoun_references)} pronouns, {len(self.attributed_statements)} statements")
        
        return results
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using basic sentence boundary detection"""
        # Simple sentence splitting - could be enhanced with more sophisticated NLP
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _identify_personnel(self, text: str, title: str = "") -> List[PersonEntity]:
        """
        Use Gemini to identify key personnel mentioned in the article.
        """
        
        prompt = f"""Analyze the following article and identify all key personnel (people) mentioned. For each person, extract:

1. Full name and any shortened versions used
2. Titles or positions held
3. Organizations they're associated with
4. Their role/relevance in the article
5. Credibility assessment (0.0-1.0) based on their position and expertise

Article Title: {title}

Article Text:
{text}

Please respond in the following JSON format:
{{
    "personnel": [
        {{
            "name": "shortened name used in article",
            "full_name": "complete name if available",
            "titles": ["title1", "title2"],
            "organizations": ["org1", "org2"],
            "role_in_article": "description of their role",
            "credibility_score": 0.8
        }}
    ]
}}

Focus on people who are quoted, make statements, or are central to the article's content."""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                import json
                data = json.loads(json_match.group())
                
                entities = []
                for i, person_data in enumerate(data.get('personnel', [])):
                    entity = PersonEntity(
                        name=person_data.get('name', ''),
                        full_name=person_data.get('full_name', person_data.get('name', '')),
                        titles=person_data.get('titles', []),
                        organizations=person_data.get('organizations', []),
                        credibility_score=person_data.get('credibility_score', 0.5),
                        role_in_article=person_data.get('role_in_article', ''),
                        first_mention_position=i  # Will be updated with actual positions
                    )
                    
                    # Find mention positions in text
                    entity.mention_positions = self._find_mention_positions(text, entity)
                    if entity.mention_positions:
                        entity.first_mention_position = entity.mention_positions[0]
                    
                    entities.append(entity)
                
                return entities
            
        except Exception as e:
            print(f"Error in personnel identification: {e}")
        
        return []
    
    def _find_mention_positions(self, text: str, entity: PersonEntity) -> List[int]:
        """Find all positions where a person is mentioned in the text"""
        positions = []
        
        # Search for various name forms
        name_variants = [entity.name, entity.full_name]
        
        # Add common name variations
        if ' ' in entity.full_name:
            parts = entity.full_name.split()
            name_variants.extend([parts[0], parts[-1]])  # First and last name
        
        for name in name_variants:
            if name:
                for match in re.finditer(re.escape(name), text, re.IGNORECASE):
                    positions.append(match.start())
        
        return sorted(list(set(positions)))
    
    def _resolve_pronouns(self, text: str) -> List[PronounReference]:
        """
        Find pronouns in text and resolve them to specific entities using context.
        """
        
        pronoun_refs = []
        words = text.split()
        
        for i, word in enumerate(words):
            # Clean word of punctuation
            clean_word = re.sub(r'[^\w]', '', word.lower())
            
            if clean_word in self.pronouns:
                # Get context window around pronoun
                start_idx = max(0, i - 10)
                end_idx = min(len(words), i + 10)
                context = ' '.join(words[start_idx:end_idx])
                
                # Find sentence containing this pronoun
                char_position = len(' '.join(words[:i]))
                sentence = self._find_sentence_containing_position(text, char_position)
                
                pronoun_ref = PronounReference(
                    pronoun=clean_word,
                    position=char_position,
                    sentence=sentence,
                    context_window=context
                )
                
                # Resolve pronoun to entity
                resolved_entity, confidence = self._resolve_pronoun_to_entity(pronoun_ref, text)
                pronoun_ref.resolved_entity = resolved_entity
                pronoun_ref.confidence_score = confidence
                
                if resolved_entity:
                    resolved_entity.pronouns_used.add(clean_word)
                
                pronoun_refs.append(pronoun_ref)
        
        return pronoun_refs
    
    def _find_sentence_containing_position(self, text: str, position: int) -> str:
        """Find the sentence that contains the given character position"""
        sentences = self._split_into_sentences(text)
        current_pos = 0
        
        for sentence in sentences:
            if current_pos <= position <= current_pos + len(sentence):
                return sentence
            current_pos += len(sentence) + 1  # +1 for space/punctuation
        
        return ""
    
    def _resolve_pronoun_to_entity(self, pronoun_ref: PronounReference, full_text: str) -> Tuple[Optional[PersonEntity], float]:
        """
        Use context and proximity to resolve a pronoun to a specific entity.
        """
        
        if not self.entities:
            return None, 0.0
        
        # Gender-based filtering
        gender_pronouns = {
            'masculine': {'he', 'him', 'his', 'himself'},
            'feminine': {'she', 'her', 'hers', 'herself'},
            'neutral': {'they', 'them', 'their', 'theirs', 'themselves'}
        }
        
        pronoun_gender = None
        for gender, pronouns in gender_pronouns.items():
            if pronoun_ref.pronoun in pronouns:
                pronoun_gender = gender
                break
        
        # Score entities based on proximity and context
        entity_scores = []
        
        for entity in self.entities:
            score = 0.0
            
            # Proximity score - closer mentions get higher scores
            if entity.mention_positions:
                closest_mention = min(entity.mention_positions, 
                                    key=lambda x: abs(x - pronoun_ref.position))
                distance = abs(closest_mention - pronoun_ref.position)
                proximity_score = max(0, 1.0 - (distance / 1000))  # Normalize by 1000 chars
                score += proximity_score * 0.4
            
            # Context relevance score
            context_score = 0.0
            context_lower = pronoun_ref.context_window.lower()
            
            # Check if entity name appears in context
            if entity.name.lower() in context_lower:
                context_score += 0.3
            
            # Check for titles/organizations in context
            for title in entity.titles:
                if title.lower() in context_lower:
                    context_score += 0.1
            
            for org in entity.organizations:
                if org.lower() in context_lower:
                    context_score += 0.1
            
            score += min(context_score, 0.4)
            
            # Recency score - more recent mentions are more likely
            recent_mentions = [pos for pos in entity.mention_positions 
                             if pos < pronoun_ref.position and pos > pronoun_ref.position - 500]
            if recent_mentions:
                recency_score = 0.2
                score += recency_score
            
            entity_scores.append((entity, score))
        
        # Sort by score and return best match
        entity_scores.sort(key=lambda x: x[1], reverse=True)
        
        if entity_scores and entity_scores[0][1] > 0.3:  # Minimum confidence threshold
            return entity_scores[0][0], entity_scores[0][1]
        
        return None, 0.0
    
    def _identify_attributed_statements(self, text: str) -> List[AttributedStatement]:
        """
        Identify statements attributed to specific people through quotes and speech patterns.
        """
        
        statements = []
        
        # Find direct quotes
        statements.extend(self._find_direct_quotes(text))
        
        # Find reported speech and paraphrased statements
        statements.extend(self._find_reported_speech(text))
        
        return statements
    
    def _find_direct_quotes(self, text: str) -> List[AttributedStatement]:
        """Find direct quotes and attribute them to speakers"""
        quotes = []
        
        for pattern in self.quote_patterns:
            for match in re.finditer(pattern, text):
                quote_text = match.group(1)
                quote_position = match.start()
                
                # Find attribution around the quote
                context_start = max(0, quote_position - 200)
                context_end = min(len(text), quote_position + len(match.group()) + 200)
                context = text[context_start:context_end]
                
                attributed_person = self._find_quote_attribution(context, quote_position)
                
                if attributed_person:
                    statement = AttributedStatement(
                        statement=quote_text,
                        attributed_person=attributed_person,
                        statement_type='direct_quote',
                        confidence_score=0.9,  # High confidence for direct quotes
                        position=quote_position,
                        context=context
                    )
                    quotes.append(statement)
        
        return quotes
    
    def _find_quote_attribution(self, context: str, quote_position: int) -> Optional[PersonEntity]:
        """Find who is attributed with a quote based on surrounding context"""
        
        # Look for attribution patterns before and after the quote
        for pattern in self.attribution_patterns:
            matches = list(re.finditer(pattern, context, re.IGNORECASE))
            
            for match in matches:
                speaker_name = match.group(1)
                
                # Find matching entity
                for entity in self.entities:
                    if (speaker_name.lower() in entity.name.lower() or 
                        speaker_name.lower() in entity.full_name.lower()):
                        return entity
        
        return None
    
    def _find_reported_speech(self, text: str) -> List[AttributedStatement]:
        """Find reported speech and paraphrased statements"""
        reported_statements = []
        
        # Patterns for reported speech
        reported_patterns = [
            r'(\w+)\s+believes?\s+that\s+([^.!?]+)',
            r'(\w+)\s+thinks?\s+that\s+([^.!?]+)',
            r'(\w+)\s+argues?\s+that\s+([^.!?]+)',
            r'(\w+)\s+suggests?\s+that\s+([^.!?]+)',
            r'(\w+)\s+maintains?\s+that\s+([^.!?]+)',
            r'(\w+)\s+contends?\s+that\s+([^.!?]+)',
            r'according\s+to\s+(\w+),\s+([^.!?]+)'
        ]
        
        for pattern in reported_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                speaker_name = match.group(1)
                statement_text = match.group(2)
                
                # Find matching entity
                attributed_person = None
                for entity in self.entities:
                    if (speaker_name.lower() in entity.name.lower() or 
                        speaker_name.lower() in entity.full_name.lower()):
                        attributed_person = entity
                        break
                
                if attributed_person:
                    statement = AttributedStatement(
                        statement=statement_text.strip(),
                        attributed_person=attributed_person,
                        statement_type='reported_speech',
                        confidence_score=0.7,
                        position=match.start(),
                        context=match.group()
                    )
                    reported_statements.append(statement)
        
        return reported_statements
    
    def _classify_and_verify_statements(self):
        """
        Classify statements as factual claims and verify their credibility.
        """
        
        for statement in self.attributed_statements:
            # Use Gemini to classify if statement contains factual claims
            is_factual = self._is_factual_claim(statement.statement)
            statement.is_factual_claim = is_factual
            
            # Verify credibility based on source
            if is_factual:
                verification_status = self._verify_statement_credibility(statement)
                statement.verification_status = verification_status
    
    def _is_factual_claim(self, statement: str) -> bool:
        """Determine if a statement contains factual claims"""
        
        prompt = f"""Analyze the following statement and determine if it contains factual claims that can be verified, or if it's primarily opinion/speculation.

Statement: "{statement}"

Respond with only "FACTUAL" if it contains verifiable facts, or "OPINION" if it's primarily opinion/speculation/belief."""

        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip().upper()
            return "FACTUAL" in result
        except:
            return False
    
    def _verify_statement_credibility(self, statement: AttributedStatement) -> str:
        """Verify the credibility of a factual statement based on the source"""
        
        # Base credibility on person's credibility score and statement type
        base_credibility = statement.attributed_person.credibility_score
        
        # Adjust based on statement type
        if statement.statement_type == 'direct_quote':
            credibility_multiplier = 1.0
        elif statement.statement_type == 'reported_speech':
            credibility_multiplier = 0.8
        else:
            credibility_multiplier = 0.6
        
        final_credibility = base_credibility * credibility_multiplier
        
        if final_credibility >= 0.8:
            return "high_credibility"
        elif final_credibility >= 0.6:
            return "medium_credibility"
        elif final_credibility >= 0.4:
            return "low_credibility"
        else:
            return "unverified"
    
    def _generate_analysis_results(self) -> Dict[str, Any]:
        """Generate comprehensive analysis results"""
        
        # Convert entities to dictionaries
        entities_data = []
        for entity in self.entities:
            entities_data.append({
                'name': entity.name,
                'full_name': entity.full_name,
                'titles': entity.titles,
                'organizations': entity.organizations,
                'credibility_score': entity.credibility_score,
                'role_in_article': entity.role_in_article,
                'mention_count': len(entity.mention_positions),
                'pronouns_used': list(entity.pronouns_used)
            })
        
        # Convert pronoun references to dictionaries
        pronoun_data = []
        for pronoun_ref in self.pronoun_references:
            pronoun_data.append({
                'pronoun': pronoun_ref.pronoun,
                'position': pronoun_ref.position,
                'sentence': pronoun_ref.sentence,
                'resolved_to': pronoun_ref.resolved_entity.name if pronoun_ref.resolved_entity else None,
                'confidence': pronoun_ref.confidence_score
            })
        
        # Convert attributed statements to dictionaries
        statements_data = []
        for statement in self.attributed_statements:
            statements_data.append({
                'statement': statement.statement,
                'attributed_to': statement.attributed_person.name,
                'statement_type': statement.statement_type,
                'is_factual_claim': statement.is_factual_claim,
                'verification_status': statement.verification_status,
                'confidence': statement.confidence_score,
                'position': statement.position
            })
        
        # Generate summary statistics
        total_pronouns = len(self.pronoun_references)
        resolved_pronouns = len([p for p in self.pronoun_references if p.resolved_entity])
        factual_statements = len([s for s in self.attributed_statements if s.is_factual_claim])
        high_credibility_facts = len([s for s in self.attributed_statements 
                                    if s.is_factual_claim and s.verification_status == "high_credibility"])
        
        return {
            'entities': entities_data,
            'pronoun_references': pronoun_data,
            'attributed_statements': statements_data,
            'summary': {
                'total_entities': len(self.entities),
                'total_pronouns': total_pronouns,
                'resolved_pronouns': resolved_pronouns,
                'resolution_rate': resolved_pronouns / total_pronouns if total_pronouns > 0 else 0,
                'total_statements': len(self.attributed_statements),
                'factual_statements': factual_statements,
                'high_credibility_facts': high_credibility_facts,
                'analysis_timestamp': datetime.now().isoformat()
            }
        }

# Test function
def test_pronoun_resolution_system():
    """Test the pronoun resolution system with sample text"""
    
    print("🧪 Testing Pronoun Resolution System")
    print("=" * 60)
    
    sample_text = """
    Dr. Sarah Johnson, the lead climate scientist at MIT, announced groundbreaking research findings yesterday. 
    She stated that "global temperatures have risen faster than previously predicted." Johnson explained that 
    her team's data shows unprecedented warming patterns. "We are seeing changes that we didn't expect for 
    another decade," she said during the press conference.
    
    Professor Michael Chen from Stanford University disagreed with some of Johnson's conclusions. He argued 
    that the methodology needs further review. "While the data is concerning, we must be cautious about 
    drawing premature conclusions," Chen told reporters. According to him, more peer review is necessary.
    
    The research team, led by Johnson, will publish their findings next month. They believe this work will 
    influence climate policy decisions globally.
    """
    
    try:
        system = PronounResolutionSystem()
        results = system.analyze_text(sample_text, "Climate Research Breakthrough")
        
        print(f"\n📊 Analysis Results:")
        print(f"Entities found: {results['summary']['total_entities']}")
        print(f"Pronouns resolved: {results['summary']['resolved_pronouns']}/{results['summary']['total_pronouns']}")
        print(f"Resolution rate: {results['summary']['resolution_rate']:.2%}")
        print(f"Attributed statements: {results['summary']['total_statements']}")
        print(f"Factual claims: {results['summary']['factual_statements']}")
        print(f"High credibility facts: {results['summary']['high_credibility_facts']}")
        
        print(f"\n👥 Identified Entities:")
        for entity in results['entities']:
            print(f"  - {entity['name']} ({entity['full_name']})")
            print(f"    Titles: {entity['titles']}")
            print(f"    Credibility: {entity['credibility_score']:.2f}")
            print(f"    Pronouns used: {entity['pronouns_used']}")
        
        print(f"\n🔗 Pronoun Resolutions:")
        for pronoun in results['pronoun_references']:
            if pronoun['resolved_to']:
                print(f"  - '{pronoun['pronoun']}' → {pronoun['resolved_to']} (confidence: {pronoun['confidence']:.2f})")
        
        print(f"\n💬 Attributed Statements:")
        for statement in results['attributed_statements']:
            print(f"  - {statement['attributed_to']}: \"{statement['statement'][:50]}...\"")
            print(f"    Type: {statement['statement_type']}, Factual: {statement['is_factual_claim']}")
            print(f"    Credibility: {statement['verification_status']}")
        
        print("\n✅ Pronoun resolution system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_pronoun_resolution_system()