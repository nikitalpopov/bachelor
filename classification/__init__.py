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

    uni = dataframe.loc[~dataframe['purpose'].isin(['test'])].copy()
    uni.loc[uni['category'] != 'university', 'category'] = 'invalid'
    # print(fg(2) + 'University' + attr(0))
    # pprint(uni)
    # print()

    sci = dataframe.loc[~dataframe['purpose'].isin(['test'])].copy()
    sci.loc[sci['category'] != 'institute', 'category'] = 'invalid'  # todo replace to 'science' when actual
    # print(fg(2) + 'Institute' + attr(0))
    # pprint(sci)
    # print()

    oth = dataframe.loc[~dataframe['purpose'].isin(['test'])].copy()
    oth.loc[oth['category'] != 'other', 'category'] = 'invalid'
    # print(fg(2) + 'Other' + attr(0))
    # pprint(oth)
    # print()

    parameters = [
        (uni, test, init.UNIVERSITY_MODEL),
        (sci, test, init.SCIENCE_MODEL),
        (oth, test, init.OTHER_MODEL)
    ]

    predicted = init.parallel_starmap(predict, parameters)

    return {
        'university': pandas.concat((test[['category', 'url', 'root']].copy().reset_index(),
                                     predicted[0].rename('prediction')), axis=1),
        'science': pandas.concat((test[['category', 'url', 'root']].copy().reset_index(),
                                  predicted[1].rename('prediction')), axis=1),
        'other': pandas.concat((test[['category', 'url', 'root']].copy().reset_index(),
                                predicted[2].rename('prediction')), axis=1)
    }
