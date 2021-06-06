# Copyright 2021 san kim
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from absl import logging
import numpy as np
import sacrebleu
import scipy.stats
import sklearn.metrics
from rouge_score import rouge_scorer
from rouge_score import scoring


# adopted from 't5' github
def accuracy(targets, predictions):
    return {"accuracy": 100*sklearn.metrics.accuracy_score(targets, predictions)}


# adopted from 't5' github
def bleu(targets, predictions):
    """Computes BLEU score.
    Args:
      targets: list of strings or list of list of strings if multiple references
        are present.
      predictions: list of strings
    Returns:
      bleu_score across all targets and predictions
    """
    if isinstance(targets[0], list):
        targets = [[x for x in target] for target in targets]
    else:
        # Need to wrap targets in another list for corpus_bleu.
        targets = [targets]

    bleu_score = sacrebleu.corpus_bleu(predictions, targets,
                                       smooth_method="exp",
                                       smooth_value=0.0,
                                       force=False,
                                       lowercase=False,
                                       tokenize="intl",
                                       use_effective_order=False)
    return {"bleu": bleu_score.score}

# adopted from 't5' github


def rouge(targets, predictions, score_keys=None):
    """Computes rouge score.
    Args:
      targets: list of strings
      predictions: list of strings
      score_keys: list of strings with the keys to compute.
    Returns:
      dict with score_key: rouge score across all targets and predictions
    """

    if score_keys is None:
        score_keys = ["rouge1", "rouge2", "rougeLsum"]
    scorer = rouge_scorer.RougeScorer(score_keys)
    aggregator = scoring.BootstrapAggregator()

    def _prepare_summary(summary):
        # Make sure the summary is not bytes-type
        # Add newlines between sentences so that rougeLsum is computed correctly.
        summary = summary.replace(" . ", " .\n")
        return summary

    for prediction, target in zip(predictions, targets):
        target = _prepare_summary(target)
        prediction = _prepare_summary(prediction)
        aggregator.add_scores(scorer.score(
            target=target, prediction=prediction))
    result = aggregator.aggregate()
    for key in score_keys:
        logging.info(
            "%s = %.2f, 95%% confidence [%.2f, %.2f]",
            key,
            result[key].mid.fmeasure*100,
            result[key].low.fmeasure*100,
            result[key].high.fmeasure*100,
        )
    return {key: result[key].mid.fmeasure*100 for key in score_keys}

# adopted from 't5' github


def pearson_corrcoef(targets, predictions):
    """Pearson correlation coefficient."""
    return {"pearson_corrcoef":
            100 * scipy.stats.pearsonr(targets, predictions)[0]}

# adopted from 't5' github


def spearman_corrcoef(targets, predictions):
    """Spearman correlation coefficient."""
    return {"spearman_corrcoef":
            100 * scipy.stats.spearmanr(targets, predictions)[0]}

# adopted from 't5' github


def exact_match(targets, predictions):
    """Computes whether the targets match predictions exactly."""
    return {"exact_match": 100 * float(np.array_equal(targets, predictions))}
