import requests

HOST = 'http://127.0.0.1:5000'

TEST_PAYLOAD = {
    'url': 'https://www.linux.org.ru/news/android/16967464?lastmod=1662582750613',
}


def test_url_shortening():
    url = HOST
    resp = requests.post(url, json=TEST_PAYLOAD)
    assert resp.ok
    assert resp.json()['url']


def test_url_expansion():
    url = HOST
    resp = requests.post(url, json=TEST_PAYLOAD)
    assert resp.ok

    generated_url = resp.json()['url']
    resp = requests.get(generated_url)
    assert resp.ok

    assert TEST_PAYLOAD['url'] == resp.json()['url']
