from __future__ import print_function
import os
import pandas as pd

def generate_lists(root_dir='output/output3', output_dir='checkpoints'):
    os.makedirs(output_dir, exist_ok=True)

    metadata_file = os.path.join(root_dir, 'metadata.csv')
    try:
        df = pd.read_csv(metadata_file)
        required_columns = ['id', 'hum', 'song', 'testing']

        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Missing required columns. CSV must contain: {required_columns}")

        train_data = df[df['testing'] == 'train']
        val_data = df[df['testing'] == 'test']

        train_lines = []
        val_lines = []

        for _, row in train_data.iterrows():
            hum_path = os.path.join('hum', row['hum']).replace('\\', '/')
            train_lines.append(f"{hum_path} {row['id']}")

            song_path = os.path.join('song', row['song']).replace('\\', '/')
            train_lines.append(f"{song_path} {row['id']}")

        for _, row in val_data.iterrows():
            hum_path = os.path.join('hum', row['hum']).replace('\\', '/')
            val_lines.append(f"{hum_path} {row['id']}")

            song_path = os.path.join('song', row['song']).replace('\\', '/')
            val_lines.append(f"{song_path} {row['id']}")

        # Remove duplicates while preserving order
        train_lines = list(dict.fromkeys(train_lines))
        val_lines = list(dict.fromkeys(val_lines))

        with open(os.path.join(output_dir, 'train_list.txt'), 'w', encoding='utf-8', errors='replace') as f:
            f.write('\n'.join(train_lines))

        with open(os.path.join(output_dir, 'val_list.txt'), 'w', encoding='utf-8', errors='replace') as f:
            f.write('\n'.join(val_lines))

        print(f"Created train list with {len(train_lines)} entries")
        print(f"Created validation list with {len(val_lines)} entries")
        print(f"Train samples: {len(train_data)}")
        print(f"Validation samples: {len(val_data)}")

    except Exception as e:
        print(f"Error processing metadata file: {e}")
        raise

class Config:
    def __init__(self):
        # Training settings
        self.train_batch_size = 32
        self.num_workers = 4
        self.max_epoch = 200
        self.lr = 1e-2
        self.weight_decay = 1e-4
        self.print_freq = 100

        # Learning rate decay settings
        self.lr_decay = 0.9
        self.lr_step = 20

        # Model settings
        self.backbone = 'resnetface'
        self.input_shape = (1, 80, 630)
        self.embedding_dim = 512

        # Data settings
        self.train_root = 'output/output3'
        self.train_list = 'checkpoints/train_list.txt'
        self.val_list = 'checkpoints/val_list.txt'

        # Save settings
        self.checkpoints_path = 'checkpoints'
