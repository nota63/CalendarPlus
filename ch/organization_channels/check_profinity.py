from better_profanity import profanity

# Initialize profanity filter
profanity.load_censor_words()

# Check if a message contains profanity
def check_message_abuse(message_content):
    if profanity.contains_profanity(message_content):
        return True
    return False