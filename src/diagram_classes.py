from plot_funcs import *


def sort_by_fst_lst(df, reverse = True):
    """
    Sort multiple lists based on a single list.
    """
    return zip(*sorted(zip(*df), key=lambda x:x[0], reverse=reverse))


def get_data(keyword_y,kommun,year,sekom,x_gender="T",keyword_x=None,y_gender=None):
    """
    Create data sets by collecting the 
    specified data for every municipality.

    Arguments:
    keyword_y -- Specifies which keyword the data points y-coordinates comes from.
    kommun    -- If a municipality has been selected, that data point should have a different colour.
    year      -- The year that the data is retrieved from.
    sekom     -- If a filter should be applied or not.
    x_gender  -- Specifies which gender the data points x-coordinates comes from.
    keyword_x -- Specifies which keyword the data points x-coordinates comes from.
    y_gender  -- Specifies which gender the data points y-coordinates comes from.
    """
    def inner_retrieve(k,v, year):
        """
        Retrieve the data for a a single municipality.
        """
        x_data = v[keyword_x][year][x_gender]
        y_data = v[keyword_y][year][y_gender]
        if x_data is not None and y_data is not None:      # Nullvärdes-filtrering.
            if no_filter or sekomgrupp == sekom_data[k]:   # Om datan ska filtreras efter sekom.
                df[3].append(y_data)
                df[1].append(x_data)
                df[2].append(k)
                if kommun == k:
                    df[0].append('red')
                else:
                    df[0].append('skyblue')

    
    df = [[],[],[],[]]                # Till index 3 läggs värden som ska plottas mot y-axeln, index 1 x-axeln, index 2 kommunnamn, index 0 färger.
    if y_gender == None:
        y_gender = x_gender
    if keyword_x == None:
        keyword_x = keyword_y

    no_filter = True
    try:
        sekomgrupp = sekom_data[kommun]
        if sekom == "Ja":
            no_filter = False
    except KeyError:                   # Om ingen kommun är vald, appliceras inget filter efter sekom.
        sekomgrupp = ""

    for k,v in mdata.items():
        try:
            inner_retrieve(k,v, year)
            show_exception_info = False
        except KeyError:           
            # Här sker problem med diagram 2 och 2019. Data från 2019 är ej upplagt på kolada för nyckeltal N15820.
            # Bör kunna hämta tidigare år mha den inre retrieve funktionen.
            show_exception_info = True
            inner_retrieve(k,v, "2018")

    if show_exception_info:
        print("Data om föräldrars utbildningsnivå saknas för 2019, visar för 2018.")

    return sort_by_fst_lst(df)

def get_single_data(dict, keyword, year, kommun=None):
    """
    Create data sets by collecting the 
    specified data for a single municipality or all of Sweden.

    Arguments:
    dict      -- Which dict one needs the data from
    keyword   -- Specifies which keyword
    year      -- The year that the data is retrieved from.
    kommun    -- If a municipality is omitted, this function returns the avarage of sweden.

    Returns int or float, and 0 if data is missing.
    """
    if kommun:
        res = dict[kommun][keyword][year]["T"]
    else:
        res = dict[keyword][year]["T"]
    if res:
        return res
    else:
        if kommun:
            print("Data saknas för kommunen", kommun, "\"", key_to_desc[keyword], "\" år", year)
        else:
            print("Data saknas för riket", "\"", key_to_desc[keyword], "\" år", year)
        return 0

def get_gendered_single_data(dict, keyword, year, kommun):
    """
    Create data sets by collecting the 
    specified data for a single municipality, divided per gender.

    Arguments:
    dict      -- Which dict one needs the data from
    keyword   -- Specifies which keyword
    year      -- The year that the data is retrieved from.
    kommun    -- The municipality that the data is retrieved from.

    Returns a pair of ints or floats, and 0 if data is missing.
    """
    women_res = dict[kommun][keyword][year]["K"]
    men_res = dict[kommun][keyword][year]["M"]
    if women_res and men_res:
        return (women_res, men_res)
    else:
        return (0, 0)

def axis_ticks(keyword):
    if keyword == "N15505":
        return 50
    return 20

def calc_sekom_avg(kommun, year, keyword):
    """ 
    Calculates the avarage of the SEKOM group which kommun belongs to,
    given a specified year and keyword. For now: weird behaviour when all data is missing.
    """

    total, kommuner = 0, 0

    for k,x in mdata.items():
        try:
            if sekom_data[k] == sekom_data[kommun]:
                current_value = x[keyword][year]["T"]
                if current_value:
                    kommuner += 1
                    total += float(current_value)
        except KeyError:
            # Upplands väsby finns inte med i sekom_data.
            continue

    try:
        return round(total / kommuner, 1)
    except ZeroDivisionError:
        print("Saknas data för alla kommuner i sekom-gruppen")
        return 0

class diagram_1(plot):
    
    def __init__(self):
        super().__init__()
    
    def update(self, keyword_desc, year, kommun, sekom):
        self.clear()

        keyword = desc_to_key[keyword_desc]
        col,m,mun,f = get_data(keyword,kommun,year,sekom,"M",y_gender="K")
        smallest = min(f + m)
        biggest = max(f + m)
        tick = axis_ticks(keyword)

        try:
            col.index("red")
        except:
            if kommun != "Ej vald":
                print("Data saknas för", kommun, "år", year)

                
        print("Visar data från", len(mun),"kommuner.")

        self.plot_line(0,0,320,320)
        self.add_scatter(m,f, mun, col, "Pojkar", "Flickor")
        self.format_layout()
        self.add_title(keyword_desc, "Pojkar", "Flickor")
        self.format_x_axis(tick, [smallest-5,biggest+5])
        self.format_y_axis(tick, [smallest-5,biggest+5])
        self.format_size(900,600)
        self.show()
        

class diagram_2(plot):
    
    def __init__(self):
        super().__init__()
        
    def update(self, keyword_desc, year, kommun, sekom):
        self.clear()

        keyword = desc_to_key[keyword_desc]
        col,ed,mun,var = get_data(keyword,kommun,year,sekom,keyword_x="N15820")
        smallest = min(var)
        biggest = max(var)
        tick = axis_ticks(keyword)

        try:
            col.index("red")
        except:
            if kommun != "Ej vald":
                print("Data saknas för", kommun, "år", year)

        print("Visar data från", len(mun),"kommuner.")
        
        self.add_scatter(ed, var, mun, col, "Föräldrars utbildningsnivå (%)", keyword_desc)
        self.format_layout(show_y_grid=True)
        self.add_title(keyword_desc, "Föräldrars utbildningsnivå (%)", keyword_desc)
        self.format_x_axis(20 ,[0,100])
        self.format_y_axis(tick, [smallest-5,biggest+5])
        self.format_size(900,600)
        self.show()

class diagram_3(plot):

    def __init__(self):
        super().__init__()

    def update(self, year, kommun, subject):
        self.clear()
        if kommun == "Ej vald":
            self.format_layout()
            self.add_title("Välj en kommun för att visa data")
            self.show()
            return

        if subject == "Engelska":
            pos_keyword = "N15574"
            neg_keyword = "N15573"

        elif subject == "Matematik":
            pos_keyword = "N15572"
            neg_keyword = "N15571"

        elif subject == "Svenska":
            pos_keyword = "N15570"
            neg_keyword = "N15569"

        kommun_over = get_single_data(mdata, pos_keyword, year, kommun)
        kommun_under =  get_single_data(mdata, neg_keyword, year, kommun)

        rike_over = get_single_data(riket_data, pos_keyword, year)
        rike_under =  get_single_data(riket_data, neg_keyword, year)

        average_pos_sekom = calc_sekom_avg(kommun,year,pos_keyword)
        average_neg_sekom = calc_sekom_avg(kommun,year,neg_keyword)


        self.add_bar([kommun, "Sekom", "Rike"],[kommun_over,
        average_pos_sekom, rike_over],["skyblue"]*3)
        

        self.add_bar([kommun, "Sekom", "Rike"],[-kommun_under,
        -average_neg_sekom, -rike_under],["tomato"]*3)

        self.add_title("Andel som fick högre respektive lägre slutbetyg än vad de skrev på nationella prov i " + subject)
        self.format_layout()
        self.show()

class diagram_4(plot):

    def __init__(self):
        super().__init__()


    def update(self, year, kommun, subject, overUnder):
        self.clear()

        if overUnder == "Betyg över NP-resultat":
            over = True
        else:
            over = False

        if subject == "Engelska":
            keyword = "N15574" if over else "N15573"

        elif subject == "Matematik":
            keyword = "N15572" if over else "N15571"
            if year == "2018":
                year = "2017"
                print("Data saknas för de nationella proven i matematik år 2018, visar för år 2017")

        elif subject == "Svenska":
            keyword = "N15570" if over else "N15569"

        pos_data = []
        municipality_name = []

        for k,x in mdata.items():
            pos_t = x[keyword][year]["T"]
            if pos_t:
                pos_data.append(pos_t)
                municipality_name.append(k)
        
        pos_data,municipality_name = sort_by_fst_lst([pos_data, municipality_name], False)
        rike_avg = get_single_data(riket_data, keyword, year)
        
        color = ["skyblue" for x in pos_data]
        try:
            color[municipality_name.index(kommun)] = "red"
        except ValueError:
            if kommun != "Ej vald":
                print("Data saknas för", kommun, "år", year)

        print("Visar data från", len(municipality_name),"kommuner.")

        self.add_bar(municipality_name,pos_data, color, False)
        self.plot_line(0,rike_avg, len(municipality_name), rike_avg,line_type="dot")

        title_snippet = "högre" if over else "lägre" 
        self.add_title("Andel som fick " + title_snippet + " slutbetyg än vad de skrev på nationella prov i " + subject)
        self.format_layout(show_y_grid=True, show_x_ticks=False)
        self.show()



class diagram_5(plot):

    def __init__(self):
        super().__init__()
    
    def update(self,kommun,year,keyword_desc):
        self.clear()

        if kommun == "Ej vald":
            self.format_layout()
            self.add_title("Välj en kommun för att visa data")
            self.show()
            return

        keyword = desc_to_key[keyword_desc]
        kommun_data = get_single_data(mdata,keyword,year,kommun)
        rike_data = get_single_data(riket_data,keyword,year)
        
        average_sekom = calc_sekom_avg(kommun,year,keyword)

        self.add_bar([kommun, "Sekom", "Rike"],[kommun_data,
        average_sekom, rike_data],["skyblue"]*3)
        self.format_layout()
        self.add_title(keyword_desc)
        self.show()
