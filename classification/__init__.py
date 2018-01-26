from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.svm import LinearSVC
from sklearn.externals import joblib
import pandas


def predict(tokens, categories, model):
    coder = HashingVectorizer()
    trn = coder.fit_transform(tokens)
    clf = LinearSVC().fit(trn, categories)
    joblib.dump(clf, model)
    tst = coder.transform(tokens.values.astype('U'))
    clf = joblib.load(model)

    return pandas.Series(clf.predict(tst))
