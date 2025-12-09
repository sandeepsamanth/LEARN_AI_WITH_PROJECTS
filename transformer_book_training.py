"""
Transformer Model Training on Book Data

This script:
1. Downloads a book (PDF or text) from the internet
2. Extracts and preprocesses the text
3. Trains a transformer encoder model on the book text
4. Tests the model to see if it can predict next words
5. Includes detailed comments for understanding
"""

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import re
from collections import Counter
import time
import urllib.request
import os

# Set random seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

print("="*80)
print("TRANSFORMER MODEL TRAINING ON BOOK DATA")
print("="*80)

# ============================================================================
# STEP 1: DOWNLOAD A BOOK FROM THE INTERNET
# ============================================================================
"""
We'll download a public domain book from Project Gutenberg.
For simplicity, we'll download a text file directly.
If you want to use a PDF, you can use PyPDF2 or pdfplumber libraries.
"""

print("\n[STEP 1] Downloading book from Project Gutenberg...")

# Download "Alice's Adventures in Wonderland" - a classic public domain book
# This is a small book, good for demonstration
book_url = "https://www.gutenberg.org/files/11/11-0.txt"
book_filename = "alice_in_wonderland.txt"

try:
    # Download the book if it doesn't exist
    if not os.path.exists(book_filename):
        print(f"Downloading book from {book_url}...")
        urllib.request.urlretrieve(book_url, book_filename)
        print(f"Book downloaded successfully: {book_filename}")
    else:
        print(f"Book already exists: {book_filename}")
    
    # Read the book text
    with open(book_filename, 'r', encoding='utf-8') as f:
        book_text = f.read()
    
    print(f"Book loaded: {len(book_text):,} characters")
    
except Exception as e:
    print(f"Error downloading book: {e}")
    print("Creating sample text for demonstration...")
    # Fallback: create sample text if download fails
    book_text = """
    Alice was beginning to get very tired of sitting by her sister on the bank, 
    and of having nothing to do: once or twice she had peeped into the book her 
    sister was reading, but it had no pictures or conversations in it, 'and what 
    is the use of a book,' thought Alice 'without pictures or conversations?'
    
    So she was considering in her own mind (as well as she could, for the hot day 
    made her feel very sleepy and stupid), whether the pleasure of making a 
    daisy-chain would be worth the trouble of getting up and picking the daisies, 
    when suddenly a White Rabbit with pink eyes ran close by her.
    
    There was nothing so very remarkable in that; nor did Alice think it so very 
    much out of the way to hear the Rabbit say to itself, 'Oh dear! Oh dear! I 
    shall be late!' (when she thought it over afterwards, it occurred to her that 
    she ought to have wondered at this, but at the time it all seemed quite natural); 
    but when the Rabbit actually took a watch out of its waistcoat-pocket, and looked 
    at it, and then hurried on, Alice started to her feet, for it flashed across her 
    mind that she had never before seen a rabbit with either a waistcoat-pocket, or 
    a watch to take out of it, and burning with curiosity, she ran across the field 
    after it, and fortunately was just in time to see it pop down a large rabbit-hole 
    under the hedge.
    """ * 50  # Repeat to have enough data

print(f"Text loaded: {len(book_text):,} characters, {len(book_text.split()):,} words")

# ============================================================================
# STEP 2: PREPROCESS THE TEXT
# ============================================================================
"""
Preprocessing involves:
- Cleaning the text (remove special characters, normalize)
- Tokenizing (split into words)
- Building vocabulary (create word-to-index mapping)
"""

print("\n[STEP 2] Preprocessing text...")

def preprocess_text(text):
    """
    Clean and normalize the text.
    
    Steps:
    1. Convert to lowercase (so "The" and "the" are the same word)
    2. Remove extra whitespace
    3. Keep only alphanumeric characters and spaces
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep spaces and basic punctuation
    # This keeps the text readable while simplifying it
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

# Clean the book text
cleaned_text = preprocess_text(book_text)
print(f"Cleaned text: {len(cleaned_text):,} characters")

# Tokenize: Split text into words
def tokenize(text):
    """
    Split text into individual words (tokens).
    Example: "hello world" -> ["hello", "world"]
    """
    return text.split()

tokens = tokenize(cleaned_text)
print(f"Total tokens (words): {len(tokens):,}")

# Build vocabulary: Create mapping from words to numbers
"""
Vocabulary is a dictionary that maps each unique word to a number.
Example: {"hello": 0, "world": 1, "the": 2, ...}

We need this because neural networks work with numbers, not words.
"""
word_counts = Counter(tokens)

# Create vocabulary with special tokens:
# <PAD> = padding token (for sequences of different lengths)
# <UNK> = unknown token (for words not in vocabulary)
# Then add all words that appear at least 2 times
vocab = ['<PAD>', '<UNK>', '<START>', '<END>'] + \
        [word for word, count in word_counts.items() if count >= 2]

word_to_idx = {word: idx for idx, word in enumerate(vocab)}
idx_to_word = {idx: word for word, idx in word_to_idx.items()}
vocab_size = len(vocab)

print(f"Vocabulary size: {vocab_size:,} unique words")
print(f"Most common words: {word_counts.most_common(10)}")

# ============================================================================
# STEP 3: CREATE TRAINING DATA (SEQUENCES)
# ============================================================================
"""
For language modeling (predicting next word), we need to create sequences.

Example:
Text: "the cat sat on the mat"
If sequence length = 5:
  Input:  ["the", "cat", "sat", "on", "the"]
  Target: ["cat", "sat", "on", "the", "mat"]

The model learns: given words [0:4], predict word [1:5]
This is called "next word prediction" or "language modeling"
"""

print("\n[STEP 3] Creating training sequences...")

def create_sequences(tokens, seq_length=50):
    """
    Create input-target pairs for training.
    
    Args:
        tokens: List of words
        seq_length: Length of each sequence (context window)
    
    Returns:
        inputs: List of input sequences
        targets: List of target sequences (shifted by 1 position)
    """
    inputs = []
    targets = []
    
    # Slide a window of size seq_length through the text
    for i in range(len(tokens) - seq_length):
        # Input: words from position i to i+seq_length-1
        input_seq = tokens[i:i+seq_length]
        
        # Target: words from position i+1 to i+seq_length (shifted by 1)
        target_seq = tokens[i+1:i+seq_length+1]
        
        # Convert words to indices (numbers)
        input_indices = [word_to_idx.get(word, word_to_idx['<UNK>']) 
                        for word in input_seq]
        target_indices = [word_to_idx.get(word, word_to_idx['<UNK>']) 
                         for word in target_seq]
        
        inputs.append(input_indices)
        targets.append(target_indices)
    
    return inputs, targets

seq_length = 50  # Context window: model sees 50 words to predict the next
inputs, targets = create_sequences(tokens, seq_length)

print(f"Created {len(inputs):,} training sequences")
print(f"Each sequence has {seq_length} words")
print(f"Example input sequence (first 10 words): {tokens[:10]}")
print(f"Example target sequence (next 10 words): {tokens[1:11]}")

# ============================================================================
# STEP 4: SPLIT INTO TRAIN AND TEST SETS
# ============================================================================
"""
We split the data so we can:
- Train on one part (learn patterns)
- Test on another part (see if it generalizes to new text)
"""

print("\n[STEP 4] Splitting into train and test sets...")

# Convert to numpy arrays for easier splitting
inputs = np.array(inputs)
targets = np.array(targets)

# Split: 80% for training, 20% for testing
split_idx = int(len(inputs) * 0.8)
X_train = inputs[:split_idx]
y_train = targets[:split_idx]
X_test = inputs[split_idx:]
y_test = targets[split_idx:]

print(f"Training sequences: {len(X_train):,}")
print(f"Test sequences: {len(X_test):,}")

# ============================================================================
# STEP 5: CREATE DATASET AND DATALOADER
# ============================================================================
"""
PyTorch uses Dataset and DataLoader to efficiently load data during training.
- Dataset: Defines how to get one sample
- DataLoader: Batches samples together for efficient training
"""

class BookDataset(Dataset):
    """
    Custom dataset class for book text sequences.
    
    This tells PyTorch how to get one training example.
    """
    def __init__(self, inputs, targets):
        self.inputs = inputs
        self.targets = targets
    
    def __len__(self):
        """Return total number of sequences"""
        return len(self.inputs)
    
    def __getitem__(self, idx):
        """
        Get one training example.
        
        Returns:
            input_seq: Sequence of word indices (input to model)
            target_seq: Sequence of word indices (what model should predict)
        """
        return torch.tensor(self.inputs[idx], dtype=torch.long), \
               torch.tensor(self.targets[idx], dtype=torch.long)

# Create datasets
train_dataset = BookDataset(X_train, y_train)
test_dataset = BookDataset(X_test, y_test)

# Create data loaders (batches data for efficient training)
batch_size = 32  # Process 32 sequences at once
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

print(f"Batch size: {batch_size}")
print(f"Training batches: {len(train_loader)}")

# ============================================================================
# STEP 6: BUILD THE TRANSFORMER ENCODER MODEL
# ============================================================================
"""
Transformer Encoder Architecture:

1. Embedding Layer:
   - Converts word indices (numbers) to dense vectors
   - Each word becomes a vector of size d_model (e.g., 128 dimensions)
   - Example: word "cat" -> [0.2, -0.5, 0.8, ..., 0.1] (128 numbers)

2. Positional Encoding:
   - Adds information about word position in sequence
   - Transformers don't naturally understand order, so we add this
   - Word at position 0 gets different encoding than word at position 10

3. Transformer Encoder Layers:
   - Multi-head Self-Attention: Each word "looks at" all other words
   - Feed-Forward Network: Processes each word independently
   - Layer Normalization: Stabilizes training
   - Residual Connections: Helps gradients flow

4. Output Layer:
   - Predicts the next word for each position
   - Output size = vocabulary size (probability for each word)
"""

class TransformerLanguageModel(nn.Module):
    """
    Transformer Encoder for Language Modeling (Next Word Prediction)
    
    This model predicts the next word in a sequence given previous words.
    """
    
    def __init__(self, vocab_size, d_model=128, nhead=4, num_layers=2,
                 dim_feedforward=256, max_seq_length=128, dropout=0.1):
        super(TransformerLanguageModel, self).__init__()
        
        self.d_model = d_model
        self.vocab_size = vocab_size
        
        # 1. EMBEDDING LAYER: Convert word indices to dense vectors
        # vocab_size = number of unique words
        # d_model = size of each word vector (embedding dimension)
        self.embedding = nn.Embedding(vocab_size, d_model)
        
        # 2. POSITIONAL ENCODING: Add position information
        # Learnable positional embeddings (alternative to fixed sinusoidal)
        self.pos_encoder = nn.Embedding(max_seq_length, d_model)
        
        # 3. TRANSFORMER ENCODER LAYERS
        # Each layer has:
        #   - Multi-head self-attention (nhead = number of attention heads)
        #   - Feed-forward network (dim_feedforward = hidden size)
        #   - Layer normalization and dropout
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,              # Embedding dimension
            nhead=nhead,                   # Number of attention heads
            dim_feedforward=dim_feedforward,  # Feed-forward network size
            dropout=dropout,               # Dropout rate (regularization)
            batch_first=True               # Batch dimension first
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, 
            num_layers=num_layers  # Stack multiple encoder layers
        )
        
        # 4. OUTPUT LAYER: Predict next word
        # Input: d_model (embedding size)
        # Output: vocab_size (probability for each word in vocabulary)
        self.output_layer = nn.Linear(d_model, vocab_size)
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        """
        Forward pass through the model.
        
        Args:
            x: Input sequences [batch_size, seq_length]
               Each number is a word index
        
        Returns:
            logits: [batch_size, seq_length, vocab_size]
                    Probability scores for each word at each position
        """
        batch_size, seq_length = x.size()
        
        # Step 1: Convert word indices to embeddings
        # x: [batch, seq] -> embeddings: [batch, seq, d_model]
        x = self.embedding(x) * np.sqrt(self.d_model)
        
        # Step 2: Add positional encoding
        # Create position indices: [0, 1, 2, ..., seq_length-1]
        positions = torch.arange(0, seq_length, device=x.device).unsqueeze(0)
        positions = positions.expand(batch_size, -1)
        
        # Add positional embeddings
        x = x + self.pos_encoder(positions)
        x = self.dropout(x)
        
        # Step 3: Pass through transformer encoder
        # The encoder applies self-attention and feed-forward layers
        x = self.transformer_encoder(x)
        
        # Step 4: Predict next word for each position
        # [batch, seq, d_model] -> [batch, seq, vocab_size]
        x = self.output_layer(x)
        
        return x

# ============================================================================
# STEP 7: INITIALIZE MODEL
# ============================================================================
print("\n[STEP 5] Initializing transformer model...")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

model = TransformerLanguageModel(
    vocab_size=vocab_size,
    d_model=128,           # Word embedding dimension (size of each word vector)
    nhead=4,               # Number of attention heads (parallel attention mechanisms)
    num_layers=2,          # Number of transformer encoder layers (depth)
    dim_feedforward=256,   # Size of feed-forward network
    max_seq_length=seq_length,
    dropout=0.1            # Dropout rate (prevents overfitting)
).to(device)

total_params = sum(p.numel() for p in model.parameters())
print(f"Model parameters: {total_params:,}")
print(f"Model architecture:")
print(f"  - Vocabulary size: {vocab_size}")
print(f"  - Embedding dimension: 128")
print(f"  - Attention heads: 4")
print(f"  - Encoder layers: 2")

# ============================================================================
# STEP 8: SETUP TRAINING
# ============================================================================
"""
Training Setup:
- Loss Function: Cross-entropy (measures difference between predicted and actual words)
- Optimizer: Adam (updates model weights to minimize loss)
- Learning Rate Scheduler: Reduces learning rate over time (helps convergence)
"""

print("\n[STEP 6] Setting up training...")

# Loss function: Cross-entropy for classification
# Compares predicted word probabilities with actual next word
criterion = nn.CrossEntropyLoss()

# Optimizer: Adam (adaptive learning rate)
# Updates model weights to minimize loss
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Learning rate scheduler: Reduces learning rate every 5 epochs
# Helps model converge better
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

num_epochs = 10  # Number of times to go through entire training set
print(f"Training for {num_epochs} epochs")

# ============================================================================
# STEP 9: TRAINING LOOP
# ============================================================================
"""
Training Process:
1. For each epoch (full pass through training data):
   a. For each batch of sequences:
      - Forward pass: Model predicts next words
      - Calculate loss: How wrong are the predictions?
      - Backward pass: Calculate gradients (how to update weights)
      - Update weights: Adjust model to make better predictions
   b. Calculate average loss and accuracy
2. Reduce learning rate (scheduler)
"""

print("\n[STEP 7] Training model...")
print("="*80)

model.train()  # Set model to training mode (enables dropout, etc.)
start_time = time.time()

for epoch in range(num_epochs):
    total_loss = 0
    total_correct = 0
    total_tokens = 0
    
    # Process each batch of sequences
    for batch_idx, (inputs, targets) in enumerate(train_loader):
        inputs = inputs.to(device)  # Move to GPU if available
        targets = targets.to(device)
        
        # FORWARD PASS: Model predicts next words
        # inputs: [batch, seq_length] - input sequences
        # outputs: [batch, seq_length, vocab_size] - predicted word probabilities
        outputs = model(inputs)
        
        # Reshape for loss calculation
        # We need: [batch*seq, vocab_size] and [batch*seq]
        outputs_flat = outputs.view(-1, vocab_size)
        targets_flat = targets.view(-1)
        
        # Calculate loss: How different are predictions from actual words?
        loss = criterion(outputs_flat, targets_flat)
        
        # BACKWARD PASS: Calculate gradients
        optimizer.zero_grad()  # Clear previous gradients
        loss.backward()        # Calculate gradients
        optimizer.step()       # Update model weights
        
        # Calculate accuracy: How many words predicted correctly?
        _, predicted = torch.max(outputs_flat, 1)
        total_correct += (predicted == targets_flat).sum().item()
        total_tokens += targets_flat.size(0)
        
        total_loss += loss.item()
    
    # Update learning rate
    scheduler.step()
    
    # Calculate average metrics for this epoch
    avg_loss = total_loss / len(train_loader)
    accuracy = 100 * total_correct / total_tokens
    
    print(f"Epoch [{epoch+1}/{num_epochs}] - "
          f"Loss: {avg_loss:.4f} - "
          f"Accuracy: {accuracy:.2f}% - "
          f"Learning Rate: {scheduler.get_last_lr()[0]:.6f}")

training_time = time.time() - start_time
print(f"\nTraining completed in {training_time:.2f} seconds")

# ============================================================================
# STEP 10: TESTING/EVALUATION
# ============================================================================
"""
Testing Process:
1. Set model to evaluation mode (disables dropout)
2. Process test data (don't update weights)
3. Calculate accuracy and perplexity
4. Show example predictions
"""

print("\n[STEP 8] Testing model on unseen data...")
print("="*80)

model.eval()  # Set to evaluation mode (disables dropout, etc.)
test_loss = 0
test_correct = 0
test_tokens = 0

with torch.no_grad():  # Don't calculate gradients (faster, saves memory)
    for inputs, targets in test_loader:
        inputs = inputs.to(device)
        targets = targets.to(device)
        
        # Forward pass
        outputs = model(inputs)
        outputs_flat = outputs.view(-1, vocab_size)
        targets_flat = targets.view(-1)
        
        # Calculate loss
        loss = criterion(outputs_flat, targets_flat)
        test_loss += loss.item()
        
        # Calculate accuracy
        _, predicted = torch.max(outputs_flat, 1)
        test_correct += (predicted == targets_flat).sum().item()
        test_tokens += targets_flat.size(0)

# Calculate metrics
avg_test_loss = test_loss / len(test_loader)
test_accuracy = 100 * test_correct / test_tokens

# Perplexity: Measure of how "surprised" the model is by the test data
# Lower perplexity = better model
perplexity = np.exp(avg_test_loss)

print(f"\nTest Results:")
print(f"  Loss: {avg_test_loss:.4f}")
print(f"  Accuracy: {test_accuracy:.2f}%")
print(f"  Perplexity: {perplexity:.2f} (lower is better)")

# ============================================================================
# STEP 11: DEMONSTRATE MODEL - GENERATE TEXT
# ============================================================================
"""
Let's test if the model actually learned by generating some text.
We'll give it a starting sequence and see what words it predicts.
"""

print("\n[STEP 9] Testing model - Generating text predictions...")
print("="*80)

def generate_text(model, seed_text, max_length=20, temperature=1.0):
    """
    Generate text by predicting next words one at a time.
    
    Args:
        model: Trained transformer model
        seed_text: Starting text (e.g., "alice was")
        max_length: How many words to generate
        temperature: Controls randomness (higher = more random)
    
    Returns:
        Generated text
    """
    model.eval()
    
    # Tokenize seed text
    seed_tokens = tokenize(preprocess_text(seed_text))
    
    # Convert to indices
    current_seq = [word_to_idx.get(word, word_to_idx['<UNK>']) 
                   for word in seed_tokens[-seq_length:]]  # Take last seq_length words
    
    generated = seed_tokens.copy()
    
    with torch.no_grad():
        for _ in range(max_length):
            # Prepare input
            if len(current_seq) < seq_length:
                # Pad if needed
                padded = current_seq + [word_to_idx['<PAD>']] * (seq_length - len(current_seq))
            else:
                padded = current_seq[-seq_length:]
            
            input_tensor = torch.tensor([padded], dtype=torch.long).to(device)
            
            # Get prediction
            output = model(input_tensor)
            
            # Get prediction for last position
            last_output = output[0, -1, :]  # [vocab_size]
            
            # Apply temperature (controls randomness)
            last_output = last_output / temperature
            
            # Convert to probabilities
            probs = torch.softmax(last_output, dim=0)
            
            # Sample next word (with some randomness)
            next_idx = torch.multinomial(probs, 1).item()
            next_word = idx_to_word[next_idx]
            
            # Avoid padding and special tokens
            if next_word in ['<PAD>', '<UNK>', '<START>', '<END>']:
                continue
            
            generated.append(next_word)
            current_seq.append(next_idx)
            
            # Keep sequence length manageable
            if len(current_seq) > seq_length:
                current_seq = current_seq[-seq_length:]
    
    return ' '.join(generated)

# Test with different seed texts
test_seeds = [
    "alice was",
    "the rabbit",
    "she thought",
]

print("\nGenerated Text Examples:")
print("-" * 80)
for seed in test_seeds:
    generated = generate_text(model, seed, max_length=15, temperature=0.8)
    print(f"\nSeed: '{seed}'")
    print(f"Generated: {generated}")
    print()

# ============================================================================
# STEP 12: SUMMARY
# ============================================================================
print("="*80)
print("TRAINING AND TESTING COMPLETE")
# ============================================================================
# STEP 13: SAVE MODEL AND VOCABULARY
# ============================================================================
"""
Save the trained model and vocabulary so we can load it later for testing.
"""
print("\n[STEP 10] Saving model and vocabulary...")

# Save model state
torch.save({
    'model_state_dict': model.state_dict(),
    'vocab_size': vocab_size,
    'd_model': 128,
    'nhead': 4,
    'num_layers': 2,
    'dim_feedforward': 256,
    'max_seq_length': seq_length,
    'word_to_idx': word_to_idx,
    'idx_to_word': idx_to_word,
    'seq_length': seq_length,
}, 'transformer_model.pth')

print("Model saved to: transformer_model.pth")
print("Vocabulary saved with model")

print("="*80)
print(f"""
SUMMARY:
--------
1. Book downloaded and processed: {len(tokens):,} words
2. Vocabulary created: {vocab_size:,} unique words
3. Training sequences: {len(X_train):,}
4. Test sequences: {len(X_test):,}
5. Model trained for {num_epochs} epochs
6. Test accuracy: {test_accuracy:.2f}%
7. Test perplexity: {perplexity:.2f}

WHAT THE MODEL LEARNED:
----------------------
The transformer encoder model learned to predict the next word in a sequence
by understanding patterns in the book text. It uses:

- Self-Attention: Each word "looks at" all other words in the sequence
  to understand context and relationships

- Positional Encoding: Understands word order (first word vs last word)

- Multi-layer Processing: Multiple transformer layers process information
  at different levels of abstraction

The model can now generate text that follows similar patterns to the book
it was trained on, though with a small dataset it may not be perfect.

NEXT STEPS (if you want to improve):
------------------------------------
1. Train on more data (larger book or multiple books)
2. Increase model size (more layers, larger embeddings)
3. Train for more epochs
4. Use pre-trained models (like GPT) and fine-tune
""")

print("="*80)

