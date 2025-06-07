from agents.orchestrator import EnhancedTravelOrchestrator

def main():
    orchestrator = EnhancedTravelOrchestrator()
    query = "Tôi muốn đi Sa Pa 3 ngày, thích trekking và cảnh đẹp núi rừng, muốn thử các món ăn đặc sản vùng cao."
    result = orchestrator.run(query)
    print(result)

if __name__ == "__main__":
    main()