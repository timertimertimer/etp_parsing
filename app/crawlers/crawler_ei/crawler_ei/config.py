data_origin = "https://ei.ru/"

types = {"bankruptcy": "1", "arrested": "2", "commercial": "6"}

params = {
    "expand": "torg,manager,prices,place,categories",
    "page": "1",
    "filter[type][]": ...,
    "filter[fuzzy]": "1",
    "filter[torgStatus][]": "1",
    "filter[maxPrice]": "44048998400",
    "filter[minDateSend]": "30",
    "filter[sortBy]": "dateDESC",
}
