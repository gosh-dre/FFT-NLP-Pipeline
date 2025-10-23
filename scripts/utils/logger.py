import logging
import os


class LogGen:
    @classmethod
    def _get_log_filepath(cls):
        log_folder = os.path.join(os.getcwd(), "fft_log")
        log_file_path = os.path.join(log_folder, "fft.log")
        return log_file_path

    @classmethod
    def loggen(cls, name):
        """
        Create logger based on config in logging.ini. All logs use the root handler.
        """
        logger = logging.getLogger(name)
        logger.handlers.clear()  # Clear existing handleris
        log_file_path = cls._get_log_filepath()
        file_handler = logging.FileHandler(filename=log_file_path, mode="a")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        return logger


def data_summary_for_logs(df):
    summary_log = {
        "wards": df.DEPARTMENT.unique().tolist(),
        "dates": df.ENTERED_DATE.unique().tolist(),
    }
    return summary_log


def sentiment_prediction_summary_for_logs(df):
    sent_lg = (
        df.groupby(["sentiment"])["Sentiment_consensus"]
        .agg(["count", "median"])
        .to_dict("index")
    )
    return sent_lg


def theme_prediction_summary_for_logs(df):
    theme_lg = (
        df.groupby(["topic"])["Theme_consensus"]
        .agg(["count", "median"])
        .to_dict("index")
    )
    return theme_lg
