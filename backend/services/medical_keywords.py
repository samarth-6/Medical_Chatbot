
MEDICAL_KEYWORDS = {
    "disease", "infection", "virus", "bacteria", "cancer", "tumor",
    "diabetes", "hypertension", "asthma", "arthritis", "pneumonia",
    "tuberculosis", "malaria", "hiv", "aids", "covid", "flu", "influenza",
    "jaundice", "hepatitis", "anemia", "leukemia", "migraine", "epilepsy",
    
    "symptom", "pain", "fever", "cough", "headache", "nausea", "vomiting",
    "fatigue", "dizziness", "rash", "swelling", "bleeding", "seizure",
    "shortness of breath", "chest pain", "abdominal pain", "back pain",
    
    "treatment", "therapy", "medication", "medicine", "drug", "prescription",
    "antibiotic", "vaccine", "vaccination", "immunization", "surgery",
    "chemotherapy", "radiation", "physical therapy", "rehabilitation",
    
    "blood", "heart", "lung", "kidney", "liver", "brain", "bone", "muscle",
    "nerve", "stomach", "intestine", "colon", "pancreas", "thyroid",
    
    "doctor", "physician", "nurse", "surgeon", "specialist", "hospital",
    "clinic", "pharmacy", "emergency room", "urgent care",
    
    "diagnosis", "test", "scan", "x-ray", "mri", "ct scan", "ultrasound",
    "blood test", "urine test", "biopsy", "screening", "examination",
    
    "health", "wellness", "nutrition", "diet", "exercise", "fitness",
    "mental health", "depression", "anxiety", "stress", "therapy",
    "counseling", "psychiatry", "psychology",
    
    "dosage", "side effect", "contraindication", "interaction", "overdose",
    "allergy", "allergic reaction", "prescription", "over the counter",
    
    "prevention", "screening", "checkup", "physical exam", "wellness visit",
    "lifestyle change", "healthy living", "quitting smoking", "weight loss",
    
    "emergency", "urgent", "ambulance", "poison", "overdose", "heart attack",
    "stroke", "seizure", "unconscious", "bleeding heavily"
}
BODY_PARTS = {
    "head", "eye", "ear", "nose", "mouth",
    "tooth", "neck", "shoulder", "arm",
    "elbow", "wrist", "hand", "finger",
    "chest", "back", "stomach", "abdomen",
    "hip", "leg", "knee", "ankle", "foot",
    "toe"
    }

SYMPTOMS = {
    "pain", "hurt", "hurts", "ache",
    "swelling", "fever", "cough",
    "nausea", "vomiting", "dizziness",
    "headache", "rash", "bleeding",
    "fatigue", "weakness"
}

COMMON_MEDICAL_PATTERNS = [
    r"my .* hurts",
    r"i have .* pain",
    r"i have a fever",
    r"my .* is swollen",
    r"i feel dizzy",
    r"i feel sick",
    r"i have a headache",
    r"i have a cough"
]