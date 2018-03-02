import init
import pandas
from colored import fg, attr
from pprint import pprint
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.svm import LinearSVC
from sklearn.externals import joblib


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


def assert_class_to_root(dataframes):
    classes = pandas.DataFrame(columns=['root', 'prediction', 'count'])
    for dataframe in dataframes:
        classes = pandas.concat(
            [classes, dataframe.groupby(['root', 'prediction'])['root'].size().reset_index(name='count')],
            axis=0, ignore_index=True).reset_index(drop=True)
    result = classes[classes['prediction'] != 'unclassified'].groupby(['root']).head(1).reset_index(drop=True)
    roots = classes.groupby(['root']).head(1).reset_index(drop=True)
    roots.loc[roots['root'].isin(result['root']), ['prediction', 'count']] = \
        result.loc[result['root'].isin(roots['root']), ['prediction', 'count']].values

    return roots


def classify(dataframe):
    test = dataframe.loc[dataframe['purpose'].isin(['test'])].copy()
    validate = dataframe.loc[dataframe['purpose'].isin(['validate'])].copy()

    uni = dataframe.loc[~dataframe['purpose'].isin(['test'])].copy()
    uni.loc[uni['category'] != init.UNIVERSITY_CATEGORY, 'category'] = 'unclassified'
    # print(fg(2) + init.UNIVERSITY_CATEGORY + attr(0))
    # pprint(uni)
    # print()

    sci = dataframe.loc[~dataframe['purpose'].isin(['test'])].copy()
    sci.loc[sci['category'] != init.SCIENCE_CATEGORY, 'category'] = 'unclassified'
    # print(fg(2) + init.SCIENCE_CATEGORY + attr(0))
    # pprint(sci)
    # print()

    oth = dataframe.loc[~dataframe['purpose'].isin(['test'])].copy()
    oth.loc[oth['category'] != init.OTHER_CATEGORY, 'category'] = 'unclassified'
    # print(fg(2) + init.OTHER_CATEGORY + attr(0))
    # pprint(oth)
    # print()

    parameters = [
        (uni, test, init.UNIVERSITY_MODEL),
        (sci, test, init.SCIENCE_MODEL),
        (oth, test, init.OTHER_MODEL)
    ]
    predicted = init.parallel(predict, parameters, mode='starmap')

    uni, sci, oth = pandas.concat((predicted[0].rename('prediction'),
                                   test[['category', 'url', 'root']].reset_index(drop=True)), axis=1), \
                    pandas.concat((predicted[1].rename('prediction'),
                                   test[['category', 'url', 'root']].reset_index(drop=True)), axis=1), \
                    pandas.concat((predicted[2].rename('prediction'),
                                   test[['category', 'url', 'root']].reset_index(drop=True)), axis=1)

    # parameters = [
    #     (init.UNIVERSITY_PREDICTED, uni),
    #     (init.SCIENCE_PREDICTED, sci),
    #     (init.OTHER_PREDICTED, oth)
    # ]
    # init.parallel(init.get_output, parameters, mode='starmap')
    writer = pandas.ExcelWriter(init.EXCEL)
    uni.to_excel(writer, init.UNIVERSITY_CATEGORY)
    sci.to_excel(writer, init.SCIENCE_CATEGORY)
    oth.to_excel(writer, init.OTHER_CATEGORY)
    results = assert_class_to_root([uni, sci, oth])
    results.to_excel(writer, 'results')
    init.get_output(init.RESULTS, results)
