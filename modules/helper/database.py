import os
import threading
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from dotenv import load_dotenv
from neo4j import GraphDatabase, Record
from neo4j.exceptions import AuthError, ClientError, ServiceUnavailable
from neo4j.time import DateTime
from neo4j.work import ResultSummary

from modules.helper.logger import setup_custom_logger


@dataclass
class Result:
    """Extractor scraping result class

    (`LogLevel`, (`msg`, `*args`), `Exception()` or `False`)

    Attributes:
        url: Uniform Resource Locator of the webpage
        index_counter: An automatic incremental counter; the number of times a webpage is encountered while crawling
        index_datetime: :class:`neo4j.time.DateTime` automatically created while crawling
        scrape_datetime: :class:`neo4j.time.DateTime` manually created while extracting
        scrape_html: HTML content of the webpage
        scrape_data: Text content of the webpage
        yara_code: Yara match status of the page"""

    url: str
    # index_counter: int = 0
    # index_datetime: DateTime = field(default_factory=DateTime.now)
    scrape_datetime: Optional[DateTime] = None
    scrape_html: Optional[str] = None
    scrape_data: Optional[str] = None
    yara_code: Optional[int] = None
    yara: Optional[Tuple[int, Tuple[str], Union[Exception, Literal[False]]]] = None
    extract: Optional[Tuple[int, Tuple[str], Union[Exception, Literal[False]]]] = None
    error: Optional[Tuple[int, Tuple[str], Union[Exception, Literal[False]]]] = None

    def __str__(self) -> str:
        return f"{{yara: {self.yara}, extract: {self.extract}, error: {self.error}}}"

    def __repr__(self) -> str:
        return f"Result(yara: {self.yara}, extract: {self.extract}, error: {self.error})"

    def dict(self) -> Dict[str, Any]:
        """Return dictionry representation for Neo4j"""
        return {
            "url": self.url,
            "scrape_datetime": self.scrape_datetime,
            "scrape_html": self.scrape_html,
            "scrape_data": self.scrape_data,
            "yara": self.yara,
        }


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
            raise
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

    def get_all_urls(self) -> List[str]:
        """
        Returns:
            List of all urls in the database
        """
        query = "MATCH (w:WebPage) RETURN w.url AS url"
        result = self.query(requested=True, query=query)
        if not result:
            return []
        records, summary = result
        all_urls = [row["url"] for row in records]
        self.logger.info("(%d ms) get_all_urls()->(%s)", summary.result_available_after, all_urls)

        return all_urls

    def get_network_structure(self) -> Dict[str, List[str]]:
        """
        Returns:
            List of all urls in the database
        """
        query = "MATCH (w1:WebPage)-[:POINTS_TO]->(w2:WebPage) RETURN w1.url AS url, COLLECT(w2.url) AS points_to"
        result = self.query(requested=True, query=query)
        network_structure = {}
        if not result:
            return network_structure
        records, summary = result
        for row in records:
            network_structure[row["url"]] = row["points_to"]
        self.logger.info("(%d ms) get_network_structure()->(%s)", summary.result_available_after, network_structure)

        return network_structure

    def get_all_scrape_data(self) -> List[str]:
        """
        Returns:
            List of all scrape_data in the database
        """
        query = "MATCH (w:WebPage) RETURN w.scrape_data AS scrape_data"
        result = self.query(requested=True, query=query)
        if not result:
            return []
        records, summary = result
        all_scrape_data = [row["scrape_data"] for row in records]
        self.logger.info("(%d ms) get_all_scrape_data()->()", summary.result_available_after)

        return all_scrape_data

    def save_all_scrape_data_as_csv(self, file_path=None) -> None:
        """
        Args:
            file_path: Location of the file to save the csv to.

        Returns:
            None
        """
        if file_path is None:
            return
        query = f'CALL apoc.export.csv.query("MATCH (w:WebPage) RETURN w.url as url, w.scrape_data AS scrape_data", "{file_path}", {{}})'
        result = self.query(requested=True, query=query)
        if not result:
            return []
        records, summary = result
        self.logger.info(
            "(%d ms) save_all_scrape_data_as_csv()->(%s)", summary.result_available_after, records[0]["file"]
        )

    def create_linkage(self, wp1_url: str, hyperlinks: List[str]) -> None:
        """Create links between a WebPage with URL `wp1_url` containing a list of `hyperlinks`

        Args:
            wp1_url: URL of WebPage 1
            hyperlinks: List of URLs in WebPage 1

        Returns:
            None
        """
        query = f"""
            UNWIND $hyperlinks AS link
            MERGE (w1:WebPage {{ url: "{wp1_url}" }})
            ON CREATE
                SET
                    w1.index_counter = 1,
                    w1.index_datetime = datetime()
            MERGE (w2:WebPage {{ url: link }})
            SET
                w2.index_counter = COALESCE(w2.index_counter, 0) + 1,
                w2.index_datetime = datetime()
            MERGE (w1)-[:POINTS_TO]->(w2)
            RETURN w1{{.url, .index_counter, .index_datetime, .scrape_datetime, .yara_code}}, w2{{.url, .index_counter, .index_datetime, .scrape_datetime, .yara_code}}"""
        result = self.query(requested=True, query=query, hyperlinks=hyperlinks)
        if not result:
            return
        records, summary = result
        self.logger.info("(%d ms) Created linkage between following items", summary.result_available_after)
        for row in records:
            self.logger.info("(%s)-[:POINTS_TO]->(%s)", row["w1"], row["w2"])

    def create_labeled_link(self, label: str, hyperlinks: Dict[str, List[str]]) -> None:
        """Create labeled links between `hyperlinks[i][0]` containing `hyperlinks[i][1]`

        Args:
            label: Label of link like "Extlink", "Mail", or "Telephone"
            hyperlinks: List of pairwise URLs with [`hyperlinks[i][0]` contains `hyperlinks[i][1]`] relationship

        Returns:
            None
        """
        query = f"""
            UNWIND keys($hyperlinks) AS parent
            WITH parent, $hyperlinks[parent] AS content
            UNWIND content AS link
            MERGE (w1:WebPage {{ url: parent }})
            ON CREATE
                SET
                    w1.index_counter = 1,
                    w1.index_datetime = datetime()
            MERGE (w2:{label} {{ url: link }})
            SET
                w2.index_counter = COALESCE(w2.index_counter, 0) + 1,
                w2.index_datetime = datetime()
            MERGE (w1)-[:CONTAINS]->(w2)
            RETURN w1{{.url, .index_counter, .index_datetime, .scrape_datetime, .yara_code}}, COLLECT(w2{{.url, .index_counter, .index_datetime}}) as w2"""
        result = self.query(requested=True, query=query, hyperlinks=hyperlinks)
        if not result:
            return
        records, summary = result
        self.logger.info(
            "(%d ms) Created '%s' relationship between following items", summary.result_available_after, label
        )
        for row in records:
            self.logger.info("(%s)-[:CONTAINS]->(%s)", row["w1"], row["w2"])

    def add_web_content(self, data: List[Result]) -> None:
        """Create labeled links between `hyperlinks[i][0]` containing `hyperlinks[i][1]`

        Args:
            label: Label of link like "Extlink", "Mail", "Telephone"
            hyperlinks: List of pairwise URLs with [`hyperlinks[i][0]` contains `hyperlinks[i][1]`] relationship

        Returns:
            None
        """
        query = """
            UNWIND $data AS page
            MERGE (w1:WebPage { url: page.url })
            ON CREATE
                SET
                    w1.index_counter = 1,
                    w1.index_datetime = datetime()
            SET
                w1.scrape_datetime = page.scrape_datetime,
                w1.scrape_data = page.scrape_data,
                w1.scrape_html = page.scrape_html,
                w1.yara = page.yara
            RETURN w1{.url, .index_counter, .index_datetime, .scrape_datetime, .yara_code}"""
        result = self.query(requested=True, query=query, data=data)
        if not result:
            return
        records, summary = result
        self.logger.info("(%d ms) Added web content for following items", summary.result_available_after)
        for row in records:
            self.logger.info("%s", row["w1"])

    def db_summary(self):
        """Summary about the database"""
        count_query = self.query(
            requested=False, query="MATCH (n) RETURN count(labels(n)) AS count, labels(n) AS labels"
        )
        return count_query

    def delete_db(self):
        """Delete all the nodes and relationships in the database"""
        self.query(requested=False, query="MATCH (n) DETACH DELETE n")
        self.logger.info("Neo4J database cleaned")

    # def __del__(self):
    #     self.shutdown()

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
    app.delete_db()

    app.create_linkage("ABC", "DEF")
    app.create_linkage("DEF", "GHI")
    app.create_linkage("DEF", "JKL")
    app.create_linkage("JKL", "ABC")

    extras = defaultdict(lambda: defaultdict(list))
    extras["Mail"]["ABC"] = ["ABC Mail", "ABC Mail2"]
    extras["Mail"]["DEF"] = ["DEF Mail", "DEF Mail2"]
    extras["Mail"]["GHI"] = ["GHI Mail", "GHI Mail2"]
    extras["Telephone"]["ABC"] = ["ABC Telephone", "ABC Telephone2"]
    extras["Telephone"]["DEF"] = ["DEF Telephone", "DEF Telephone2"]
    extras["Telephone"]["GHI"] = ["GHI Telephone", "GHI Telephone2"]
    for label, data in extras.items():
        app.create_labeled_link(label, data)

    data = [
        Result(
            url="ABC", scrape_datetime=DateTime.now(), scrape_data="ABC DATA", scrape_html="ABC HTML", yara=0
        ).dict(),
        Result(url="DEF", scrape_datetime=DateTime.now(), scrape_data="DEF DATA", scrape_html="DEF HTML").dict(),
        Result(
            url="GHI", scrape_datetime=DateTime.now(), scrape_data="GHI DATA", scrape_html="GHI HTML", yara=1
        ).dict(),
    ]
    app.add_web_content(data=data)

    app.get_network_structure()
    app.save_all_scrape_data_as_csv(file_path="/home/proxzima/Documents/PROxZIMA/DarkSpider/output/dataset.csv")
    app.shutdown()
