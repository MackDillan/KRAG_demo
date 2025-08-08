import os
import json
import time
from langchain_neo4j import Neo4jGraph
from neo4j.exceptions import ServiceUnavailable


NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4jneo4j")

def connect_to_neo4j(max_retries=10, retry_delay_seconds=5):
    """Establishes a connection to Neo4j with retry logic."""
    print(f"Attempting to connect to Neo4j at {NEO4J_URI}...")
    graph = None
    for i in range(max_retries):
        try:
            graph = Neo4jGraph(
                url=NEO4J_URI,
                username=NEO4J_USERNAME,
                password=NEO4J_PASSWORD,
            )
            # Perform a simple query to check connection
            graph.query("RETURN 1")
            print("Successfully connected to Neo4j.")
            return graph
        except ServiceUnavailable as e:
            print(f"Neo4j connection attempt {i+1}/{max_retries} failed (ServiceUnavailable): {e}")
            if i < max_retries - 1:
                print(f"Retrying in {retry_delay_seconds} seconds...")
                time.sleep(retry_delay_seconds)
            else:
                print("Max retries reached. Could not connect to Neo4j. Exiting.")
                exit(1)
        except Exception as e:
            print(f"An unexpected error occurred during connection attempt {i+1}/{max_retries}: {e}")
            if i < max_retries - 1:
                print(f"Retrying in {retry_delay_seconds} seconds...")
                time.sleep(retry_delay_seconds)
            else:
                print("Max retries reached. Could not connect to Neo4j. Exiting.")
                exit(1)
    return None

def create_paper_data(graph, paper_data):
    """
    Inserts or merges paper data into Neo4j using a single Cypher query.
    This is generally more efficient than multiple small transactions.
    """
    query = """
    MERGE (p:Paper {id: $id})
    SET p.title = $title,
        p.abstract = $abstract

    WITH p, $lang AS lang, $year AS year, $fos AS fos, $keywords AS keywords, $references AS references

    FOREACH (l_code IN CASE WHEN lang IS NOT NULL THEN [lang] ELSE [] END |
        MERGE (l:Language {code: l_code})
        MERGE (p)-[:WRITTEN_IN]->(l)
    )

    FOREACH (y_value IN CASE WHEN year IS NOT NULL THEN [year] ELSE [] END |
        MERGE (y:Year {value: y_value})
        MERGE (p)-[:PUBLISHED_IN]->(y)
    )

    FOREACH (fos_name IN fos |
        MERGE (f:FieldOfStudy {name: fos_name})
        MERGE (p)-[:HAS_FIELD]->(f)
    )

    FOREACH (kw_name IN keywords |
        MERGE (k:Keyword {name: kw_name})
        MERGE (p)-[:HAS_KEYWORD]->(k)
    )

    FOREACH (ref_id_str IN references |
        MERGE (target:Paper {id: ref_id_str})
        MERGE (p)-[:CITES]->(target)
    )
    """
    graph.query(query, paper_data)

def seed_database_from_file(file_path='output.txt', batch_size=100):
    """
    Reads data from a file and seeds the Neo4j database in batches.
    """
    graph = connect_to_neo4j()
    if not graph:
        print("Failed to get a Neo4j graph connection.")
        return

    print(f"\nStarting database seeding from {file_path}...")
    papers_batch = []
    processed_count = 0
    start_time = time.time()

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                try:
                    paper = json.loads(line)
                    # Ensure all expected keys are present, even if empty/None
                    paper_formatted = {
                        "id": str(paper.get('id')), # Ensure ID is string
                        "title": paper.get('title'),
                        "abstract": paper.get('abstract'),
                        "lang": paper.get('lang'),
                        "year": paper.get('year'),
                        "fos": paper.get('fos', []),
                        "keywords": paper.get('keywords', []),
                        "references": [str(ref) for ref in paper.get('references', [])] # Ensure references are strings
                    }
                    papers_batch.append(paper_formatted)

                    if len(papers_batch) >= batch_size:
                        print(f"Processing batch of {len(papers_batch)} papers (total: {processed_count + len(papers_batch)})...")
                        for p_data in papers_batch:
                            create_paper_data(graph, p_data)
                        processed_count += len(papers_batch)
                        papers_batch = [] # Clear the batch

                except json.JSONDecodeError as e:
                    print(f"Skipping line {line_num} due to JSON error: {e} - Line content: {line.strip()[:100]}...")
                except Exception as e:
                    print(f"Error processing line {line_num}: {e} - Line content: {line.strip()[:100]}...")
                    # Decide whether to continue or stop on error

            # Process any remaining papers in the last batch
            if papers_batch:
                print(f"Processing final batch of {len(papers_batch)} papers (total: {processed_count + len(papers_batch)})...")
                for p_data in papers_batch:
                    create_paper_data(graph, p_data)
                processed_count += len(papers_batch)

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during file processing: {e}")
        exit(1)

    end_time = time.time()
    print(f"\nDatabase seeding complete. Processed {processed_count} papers in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    seed_database_from_file(file_path='output.txt')