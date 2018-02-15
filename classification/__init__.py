import init
import pandas
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.svm import LinearSVC
from sklearn.externals import joblib
from pprint import pprint
from colored import fg, attr


def predict(train, test, model):
    """Train classifier and predict results
        :param train:
        :param test:
        :param model:
    """
    coder = HashingVectorizer()
    trn = coder.fit_transform(train.text)
    clf = LinearSVC().fit(trn, train.category)
    joblib.dump(clf, model)
    tst = coder.transform(test.text.values.astype('U'))
    clf = joblib.load(model)

    return pandas.Series(clf.predict(tst))


def classify(dataframe):
    test = dataframe.loc[dataframe['purpose'].isin(['test'])].copy()
    validate = dataframe.loc[dataframe['purpose'].isin(['validate'])].copy()

    # uni = dataframe.copy()
    uni = dataframe.loc[~dataframe['purpose'].isin(['test'])].copy()
    uni.loc[uni['category'] != 'university', 'category'] = 'invalid'
    print(fg(2) + 'University' + attr(0))
    pprint(uni)
    print()

    # sci = dataframe.copy()
    sci = dataframe.loc[~dataframe['purpose'].isin(['test'])].copy()
    sci.loc[sci['category'] != 'institute', 'category'] = 'invalid'  # todo replace to 'science' when actual
    print(fg(2) + 'Institute' + attr(0))
    pprint(sci)
    print()

    # oth = dataframe.copy()
    oth = dataframe.loc[~dataframe['purpose'].isin(['test'])].copy()
    oth.loc[oth['category'] != 'other', 'category'] = 'invalid'
    print(fg(2) + 'Other' + attr(0))
    pprint(oth)
    print()

    parameters = [
        (uni, test, init.UNIVERSITY_MODEL),
        (sci, test, init.SCIENCE_MODEL),
        (oth, test, init.OTHER_MODEL)
    ]

    predicted = init.parallel_starmap(predict, parameters)

    print(fg(2) + 'Predicted' + attr(0))
    pprint(predicted)

    return {
        'university': (predicted[0], test.loc[test['category'] == 'university', 'url']),
        'science': (predicted[1], test.loc[test['category'] == 'university', 'url']),
        'other': (predicted[2], test.loc[test['category'] == 'university', 'url'])
    }
