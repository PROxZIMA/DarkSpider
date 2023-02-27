import os
import threading
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from neo4j import GraphDatabase, Record
from neo4j.exceptions import AuthError, ClientError, ServiceUnavailable
from neo4j.time import DateTime
from neo4j.work import ResultSummary

from modules.helper.logger import setup_custom_logger


@dataclass
class WebPage:
    """A Webpage

    Attributes:
        url: Uniform Resource Locator of the webpage
        index_counter: An automatic incremental counter; the number of times a webpage is encountered while crawling
        index_datetime: :class:`neo4j.time.DateTime` automatically created while crawling
        scrape_datetime: :class:`neo4j.time.DateTime` manually created while extracting
        scrape_html: HTML content of the webpage
        scrape_data: Text content of the webpage
    """

    url: str
    index_counter: int = 0
    index_datetime: DateTime = field(default_factory=DateTime.now)
    scrape_datetime: Optional[DateTime] = None
    scrape_html: Optional[str] = None
    scrape_data: Optional[str] = None


class DatabaseManager:
    """Instantiates the Neo4J Graph Database

    Attributes:
        out_path: Output path for the log files
        server: URI examples: "bolt://localhost:7687", "neo4j+s://xxx.databases.neo4j.io"
        user: database user
        password: database password
    """

    server = None
    user = None
    password = None
    driver = None
    logger = None
    write_lock = threading.Lock()
    labels = [("WebPage", "url")]
    keys = {"WebPage": ["url", "index_counter", "index_datetime", "scrape_datetime", "scrape_html", "scrape_data"]}

    def __init__(self, out_path: str, server: str, user: str = None, password: str = None):
        self.logger = setup_custom_logger(
            name="dblog", filename=os.path.join(out_path, "db.log"), verbose_=True, filelog=True, screenlog=False
        )
        self.server = server
        self.user = user
        self.password = password
        self.get_graph_driver(self.server, self.user, self.password)
        self.create_indexes()

    @staticmethod
    def _transaction_function(tx, **kwargs):
        result = tx.run(kwargs.pop("query"), **kwargs)
        records = list(result)  # a list of Record objects
        summary = result.consume()
        return records, summary

    def query(self, requested: bool = False, **kwargs) -> Optional[Tuple[List[Record], ResultSummary]]:
        """execute a query into the graph"""
        # self.write_lock.acquire()
        records = []
        summary: ResultSummary = None
        _query = kwargs.get("query", None)
        try:
            with self.driver.session(database="neo4j") as session:
                records, summary = session.execute_write(transaction_function=self._transaction_function, **kwargs)
        except ClientError as e:
            if str(e.message).startswith("An equivalent index"):
                raise
            self.logger.error("ClientError :: Transaction failed with %s", e.message, exc_info=e)
        except Exception as e:
            self.logger.error("Error :: Transaction failed. Query :: %s", _query, exc_info=e)
        finally:
            # self.write_lock.release()
            if requested and records and summary:
                return records, summary

    def get_graph_driver(self, uri: str, username: str, password: str) -> GraphDatabase:
        """sets up graph client"""
        try:
            auth = None
            if username and password:
                auth = (username, password)
            self.driver = GraphDatabase.driver(uri, auth=auth, encrypted=False)
            self.driver.verify_connectivity()
            self.logger.info("Neo4J database connectivity successful")
        except AuthError as e:
            self.logger.error("AuthError :: Could not authenticate to Neo4j database server", exc_info=e)
        except Exception as e:
            self.logger.error("Error :: Failed to create graph client", exc_info=e)
            raise

    def create_indexes(self):
        """create indexes for faster lookup"""
        for label, _property in self.labels:
            query = f"CREATE INDEX IF NOT EXISTS FOR (n:{label}) ON (n.{_property})"
            try:
                self.query(requested=False, query=query)
            except ClientError:
                pass

    def create_linkage(self, wp1_url: str, hyperlinks: List[str]) -> None:
        """Create links between a WebPage with URL `wp1_url` containing a list of `hyperlinks`

        Args:
            wp1_url: URL of WebPage 1
            hyperlinks: List of URLs in WebPage 1

        Returns:
            None
        """
        query = """
            MERGE (w1:WebPage { url: $wp1_url })
            ON CREATE
                SET
                    w1.index_counter = 1,
                    w1.index_datetime = datetime()
            FOREACH (link IN $hyperlinks |
                MERGE (w2:WebPage { url: link })
                SET
                    w2.index_counter = COALESCE(w2.index_counter, 0) + 1,
                    w2.index_datetime = datetime()
                MERGE (w1)-[:POINTS_TO]->(w2)
            )
            RETURN w1, $hyperlinks as hyperlinks"""
        result = self.query(requested=True, query=query, wp1_url=wp1_url, hyperlinks=hyperlinks)
        if not result:
            return
        records, summary = result
        for row in records:
            self.logger.info(
                "(%d ms) (%s)-[:POINTS_TO]->(%s)", summary.result_available_after, row["w1"], row["hyperlinks"]
            )

    def db_summary(self):
        """Summary about the database"""
        count_query = self.query(
            requested=False, query="MATCH (n) RETURN count(labels(n)) AS count, labels(n) AS labels"
        )
        return count_query

    def delete_db(self):
        """Delete all the nodes and relationships in the database"""
        self.query(requested=False, query="MATCH (n) DETACH DELETE n")

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        """Close the driver connection"""
        if self.driver:
            self.logger.info("Closing the Neo4J session")
            self.driver.close()


if __name__ == "__main__":
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    load_dotenv()

    app = DatabaseManager(
        "output",
        os.environ.get("NEO4J_SERVER"),
        os.environ.get("NEO4J_USER"),
        os.environ.get("NEO4J_PASSWORD"),
    )
    app.create_linkage("ABC", "DEF")
    app.create_linkage("DEF", "GHI")
    app.create_linkage("DEF", "JKL")
    app.create_linkage("JKL", "ABC")
    app.close()
