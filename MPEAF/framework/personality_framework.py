class PersonalityFramework:
    def __init__(self):
        """Initialize multi-level personality framework"""
        # First level: Big Five personality dimensions
        self.big_five_dimensions = {
            "O": "Openness",
            "C": "Conscientiousness",
            "E": "Extraversion",
            "A": "Agreeableness",
            "N": "Neuroticism"
        }
        
        # Second level: 30 personality sub-traits
        self.traits = {
            # Openness (O)
            "O1": {"name": "Fantasy", "dimension": "O"},
            "O2": {"name": "Aesthetics", "dimension": "O"},
            "O3": {"name": "Feelings", "dimension": "O"},
            "O4": {"name": "Actions", "dimension": "O"},
            "O5": {"name": "Ideas", "dimension": "O"},
            "O6": {"name": "Values", "dimension": "O"},
            
            # Conscientiousness (C)
            "C1": {"name": "Competence", "dimension": "C"},
            "C2": {"name": "Order", "dimension": "C"},
            "C3": {"name": "Dutifulness", "dimension": "C"},
            "C4": {"name": "Achievement Striving", "dimension": "C"},
            "C5": {"name": "Self-Discipline", "dimension": "C"},
            "C6": {"name": "Deliberation", "dimension": "C"},
            
            # Extraversion (E)
            "E1": {"name": "Warmth", "dimension": "E"},
            "E2": {"name": "Gregariousness", "dimension": "E"},
            "E3": {"name": "Assertiveness", "dimension": "E"},
            "E4": {"name": "Activity", "dimension": "E"},
            "E5": {"name": "Excitement-Seeking", "dimension": "E"},
            "E6": {"name": "Positive Emotions", "dimension": "E"},
            
            # Agreeableness (A)
            "A1": {"name": "Trust", "dimension": "A"},
            "A2": {"name": "Straightforwardness", "dimension": "A"},
            "A3": {"name": "Altruism", "dimension": "A"},
            "A4": {"name": "Compliance", "dimension": "A"},
            "A5": {"name": "Modesty", "dimension": "A"},
            "A6": {"name": "Tender-Mindedness", "dimension": "A"},
            
            # Neuroticism (N)
            "N1": {"name": "Anxiety", "dimension": "N"},
            "N2": {"name": "Angry Hostility", "dimension": "N"},
            "N3": {"name": "Depression", "dimension": "N"},
            "N4": {"name": "Self-Consciousness", "dimension": "N"},
            "N5": {"name": "Impulsiveness", "dimension": "N"},
            "N6": {"name": "Vulnerability", "dimension": "N"}
        }
        
        # Third level: Linguistic markers
        self.linguistic_markers = {
            # Openness dimension markers
            "O1": [
                "Using imaginative descriptions and hypothetical scenarios",
                "Discussing creative activities or dreams",
                "Mentioning fictional worlds or scenes"
            ],
            "O2": [
                "Discussing art, aesthetics, or natural beauty",
                "Using rich descriptive vocabulary",
                "Expressing appreciation for beauty"
            ],
            "O3": [
                "Expressing emotional depth and intensity",
                "Sharing inner feelings",
                "Reflecting on emotional and mood states"
            ],
            "O4": [
                "Discussing new experiences or attempts",
                "Expressing preference for diversity",
                "Mentioning unconventional activities"
            ],
            "O5": [
                "Asking deep questions or philosophical thoughts",
                "Exploring abstract concepts",
                "Analyzing and reasoning through complex problems"
            ],
            "O6": [
                "Discussing moral or ethical issues",
                "Questioning traditional ideas or norms",
                "Expressing non-traditional values"
            ],
            
            # Conscientiousness dimension markers
            "C1": [
                "Expressing confidence and capability",
                "Discussing personal achievements",
                "Providing detailed, organized explanations"
            ],
            "C2": [
                "Using ordered structure and lists",
                "Focusing on details and precision",
                "Emphasizing planning and organization"
            ],
            "C3": [
                "Emphasizing sense of duty and obligation",
                "Expressing importance of keeping promises",
                "Discussing moral and ethical guidelines"
            ],
            "C4": [
                "Setting clear goals",
                "Expressing ambition and drive",
                "Discussing effort and success"
            ],
            "C5": [
                "Emphasizing self-control and perseverance",
                "Discussing ability to complete tasks",
                "Avoiding distractions or procrastination"
            ],
            "C6": [
                "Demonstrating thoughtful decision-making processes",
                "Considering pros and cons of multiple options",
                "Avoiding impulsive behavior"
            ],
            
            # Extraversion dimension markers
            "E1": [
                "Expressing friendliness and enthusiasm",
                "Focusing on connections with others",
                "Using warm, affectionate language"
            ],
            "E2": [
                "Mentioning social activities and groups",
                "Expressing enjoyment of social occasions",
                "Avoiding solitude"
            ],
            "E3": [
                "Using direct, assertive language",
                "Expressing opinions without hesitation",
                "Guiding conversation or making suggestions"
            ],
            "E4": [
                "Discussing physical activities and high-energy pursuits",
                "Portraying busy and active lifestyle",
                "Using dynamic vocabulary"
            ],
            "E5": [
                "Seeking stimulation and adventure",
                "Expressing interest in novel experiences",
                "Discussing exciting activities"
            ],
            "E6": [
                "Expressing optimism and joy",
                "Using positive emotional vocabulary",
                "Sharing happy things and laughter"
            ],
            
            # Agreeableness dimension markers
            "A1": [
                "Expressing trust in others",
                "Assuming others have good intentions",
                "Willingness to share personal information"
            ],
            "A2": [
                "Direct, honest expression",
                "Avoiding manipulation or concealment",
                "Expressing genuine thoughts"
            ],
            "A3": [
                "Offering help or support",
                "Expressing concern for others' well-being",
                "Engaging in selfless acts"
            ],
            "A4": [
                "Avoiding conflict and arguments",
                "Compromising or yielding",
                "Displaying mild manner"
            ],
            "A5": [
                "Avoiding boasting or excessive confidence",
                "Downplaying personal achievements",
                "Acknowledging personal limitations"
            ],
            "A6": [
                "Expressing sympathy and understanding",
                "Focusing on others' emotional needs",
                "Using gentle, supportive language"
            ],
            
            # Neuroticism dimension markers
            "N1": [
                "Expressing worry and unease",
                "Imagining negative outcomes",
                "Seeking reassurance"
            ],
            "N2": [
                "Expressing anger or dissatisfaction",
                "Using intense or aggressive language",
                "Negative evaluation of others or situations"
            ],
            "N3": [
                "Expressing pessimism and hopelessness",
                "Focusing on negative aspects",
                "Using negative emotional vocabulary"
            ],
            "N4": [
                "Displaying social anxiety or awkwardness",
                "Worrying about others' evaluations",
                "Self-criticism"
            ],
            "N5": [
                "Displaying impulsive decision making",
                "Difficulty resisting temptation",
                "Expressing desire for immediate gratification"
            ],
            "N6": [
                "Displaying difficulty coping under pressure",
                "Seeking help with problems",
                "Showing overwhelm in face of challenges"
            ]
        }
    
    def get_dimension_traits(self, dimension):
        """Get all sub-traits for a specific dimension"""
        return {code: trait for code, trait in self.traits.items() if trait['dimension'] == dimension}
    
    def get_trait_markers(self, trait_code):
        """Get linguistic markers for a specific sub-trait"""
        return self.linguistic_markers.get(trait_code, [])
    
    def get_all_traits_with_markers(self):
        """Get all sub-traits with their linguistic markers"""
        result = {}
        for trait_code, trait_info in self.traits.items():
            result[trait_code] = {
                "name": trait_info["name"],
                "dimension": trait_info["dimension"],
                "dimension_name": self.big_five_dimensions[trait_info["dimension"]],
                "markers": self.get_trait_markers(trait_code)
            }
        return result