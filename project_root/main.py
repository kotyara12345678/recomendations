from trainer.dataset import load_dataset
from trainer.trainer import train_model

def main():
    print("🚀 Trainer started")

    texts = load_dataset()
    train_model(texts)

    print("✅ Training finished")

if __name__ == "__main__":
    main()