graph TD
    A[Data Sources] --> B[Data Ingestion Layer]
    B --> C[Threat Detection Engine]
    C --> D[Response Orchestration]
    C --> E[Storage Layer]
    E --> F[Monitoring and Analytics]
    D --> F