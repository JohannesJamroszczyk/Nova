import urllib
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from ttkthemes import themed_tk as tk
from PIL import ImageTk, Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import inflection
import re
import sys
import os
from bs4.element import Comment
from bs4 import BeautifulSoup
from urllib.request import urlopen

print("commit")

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


matplotlib.use("TkAgg")

# GUI
# Loading Screen
loading = Tk()
loading.overrideredirect(True)
loading.geometry("592x428+450+220")
loading.minsize(361, 265)
loading_image = ImageTk.PhotoImage(Image.open(resource_path("images/loader.tif")))
loading_panel = Label(loading, image=loading_image, borderwidth=0, compound="none",
                      highlightthickness=0, padx=0, pady=0)
loading_panel.pack()
loading.after(4000, loading.destroy)
loading.mainloop()

# Main Window
root = tk.ThemedTk()
root.get_themes()
root.set_theme("arc")
root.title("Nova")
root.iconbitmap(resource_path("images/icon.ico"))
root.configure(bg='white')
root.geometry("1280x700+200+45")
root.minsize(1000, 600)

# Menubar
menubar = Menu(root)
root.config(menu=menubar)
file_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)
menubar.add_cascade(label="Edit", menu=file_menu)
menubar.add_cascade(label="View", menu=file_menu)
menubar.add_cascade(label="Window", menu=file_menu)
menubar.add_cascade(label="About", menu=file_menu)
file_menu.add_command(label="Exit", command=root.destroy)

# Predefining a Frame and Toolbar
frm = None
toolbar = None

# Quiting Function
def close_window():
    root.destroy()

urlmarker = 0  # Indicates wheather URL or File is used

# Slider Function
def slide():
    global count_criteria
    onCreate_label.config(text="Word minimum is set to " + str(int(word_count_slider.get())), bg='grey30',
                          fg='white', font='verdana 8')
    count_criteria = int(word_count_slider.get())
    analyse_button.place(x=20, y=300, anchor='w', height=30, width=210)


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


# Text Analysis Function

def analysis():
    loadingsymbol = ImageTk.PhotoImage(Image.open(resource_path("images/new/sand_clock.png")))
    loading_panel = Label(root, image=loadingsymbol, borderwidth=0, compound="none", highlightthickness=0, padx=0,
                          pady=0)
    loading_panel.place(x=1150, y=60, anchor='w')

    print(urlmarker)
    global link, input_string
    # checking whether frm and toolbar exist and, if so, removing them
    global frm, toolbar
    if frm is not None and frm.winfo_exists():
        if toolbar is not None and toolbar.winfo_exists():
            frm.destroy()
            toolbar.destroy()

    # reading the input text using the chosen path in _search()_
    if urlmarker == 0:
        input_txt = open(source, "r", encoding="utf8")
        tag_cleaner = re.compile('<.*?>|/&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')  # removing tags from input text
        input_string = re.sub(tag_cleaner, '', input_txt.read())  # defining tag-cleaned input string
    elif urlmarker == 1:
        input_string = text_from_html(urlopen(link).read())

    def text2word(text):  # removing all special Characters
        result = re.findall('[-\w]+', text.lower())
        return result

    full_string_list = text2word(input_string)

    no_numbers = [re.sub('[0-9]', '', i) for i in full_string_list]
    # Defining and applying word length cut off
    maximum = 25  # input("Choose upper cut for word length: ")
    minimum = 3  # input("Choose lower cut for word length: ")
    input_words = [word for word in no_numbers if int(maximum) > len(word) > int(minimum)]

    # importing stop word txt
    stop_txt = open(resource_path("stop-en.txt"), "r", True, 'utf-8')
    stop_words_list = stop_txt.read().split('\n')  # converting stop word string to list
    low_list = []
    for x in stop_words_list:
        low_list.append(x.lower())

    for word in list(input_words):
        if word in low_list or word.isdigit():  # Wipe stop words and string digits
            input_words.remove(word)

    output_words = [inflection.singularize(plural) for plural in
                    input_words]  # Combines singulars and plurals into singulars

    # count_criteria = 10 # input("Choose count minimum: ")  # Define or take user input for count exclusion criteria
    counted_words = Counter(output_words)
    exclusion_list = []

    for word in counted_words:
        if urlmarker == 0:
            if counted_words[word] < int(count_criteria):
                exclusion_list.append(word)
        elif urlmarker == 1:
            if counted_words[word] < int(count_criteria) or word in link:
                exclusion_list.append(word)
    inclusion_list = []
    for word in output_words:
        if word not in exclusion_list:
            inclusion_list.append(word)  # Makes list of all words, not in exclusion list

    inclusion_list = [x.title() for x in inclusion_list]  # capitalizes/lowers/titles displayed words
    ordered_inclusion_list = [item for items, c in Counter(inclusion_list).most_common()
                              for item in [items] * c]
    counted_words = Counter(ordered_inclusion_list)
    final_dictionary = {i: ordered_inclusion_list.count(i) for i in counted_words}  # ordered and counted inclusion list
    key_list = list(final_dictionary.keys())  # Lists the words in descending (count)order
    counts_list = list(final_dictionary.values())  # Lists counts of the words in descending order

    print(final_dictionary)

    # Coocurences
    bigrams = Counter()
    for previous, current in zip(inclusion_list, inclusion_list[1:]):  # Checking for (vica-versa) bigrams
        opt1 = f"{previous}", f"{current}"
        opt2 = f"{current}", f"{previous}"
        if opt2 not in bigrams:
            bigrams[opt1] += 1
            continue
        bigrams[opt2] += 1  #
    coocurences = dict(bigrams)

    for key in list(coocurences.keys()):  # Checking for (same-same) bigrams
        if key[0] == key[1]:
            del coocurences[key]

    total = sum(coocurences.values())
    new_dict = {k: (v / total) * 100 for k, v in coocurences.items()}

    f = Figure(figsize=(6.5, 4), dpi=165)
    a = f.add_subplot(111)
    graph = nx.Graph()
    # plt.style.use('dark_background')

    for x, y in new_dict.items():
        graph.add_weighted_edges_from([[str(x[0]), str(x[1]), 100 * y]])

    messy_a_counts = list(map(final_dictionary.get, list(graph.nodes)))
    node_size_list = []
    for i in messy_a_counts:
        node_size_list.append((i / sum(counts_list)) * 4000)  # creates the node size list

    pos = nx.spring_layout(graph, weight='weight')

    node_color_map = []
    for node in node_size_list:
        if 0 < (node / 4000) < 0.001:
            node_color_map.append('green')
        elif 0.001 < (node / 4000) < 0.003:
            node_color_map.append('lawngreen')
        elif 0.003 < (node / 4000) < 0.005:
            node_color_map.append('springgreen')
        elif 0.005 < (node / 4000) < 0.015:
            node_color_map.append('aquamarine')
        elif 0.015 < (node / 4000) < 0.02:
            node_color_map.append('cyan')
        elif 0.02 < (node / 4000) < 0.025:
            node_color_map.append('deepskyblue')
        elif 0.025 < (node / 4000) < 0.07:
            node_color_map.append('dodgerblue')
        elif 0.07 < (node / 4000) or node == max(node_size_list):
            node_color_map.append('red')
        else:
            node_color_map.append('yellow')

    # edge_color_map = []
    # for edge in edge_width_list:
    # if 0 < (edge/250) < 0.0003:
    # edge_color_map.append('grey')
    # elif 0.0003 < (edge/250) < 0.004:
    # edge_color_map.append('grey')
    # elif 0.004 < (edge/250):
    # edge_color_map.append('grey')

    nx.draw_networkx_nodes(graph, pos, node_size=node_size_list, node_color=node_size_list, alpha=0.9, node_shape='o',
                           cmap=plt.cm.Paired, ax=a)
    nx.draw_networkx_edges(graph, pos, edgelist=new_dict.keys(), width=[i for i in new_dict.values()],
                           edge_color='grey', alpha=0.2, ax=a)
    nx.draw_networkx_labels(graph, pos, font_size=9, font_family='Verdana', font_color='black', ax=a)

    a.axis('off')
    plt.savefig("graph.jpg", dpi=200)
    # plt.figure(figsize=(9, 5))
    # plt.subplot(132)
    # names = list(reversed(key_list))
    # values = list(reversed(counts_list))
    # plt.scatter(values, names)

    global text_length
    global keyword_number
    global mode
    global bigram_number

    text_length = str(len(full_string_list))
    keyword_number = str(len(key_list))

    if len(key_list) == 1:
        maxNode = "-"
        bigram_number = "0"
        mode = key_list[0]

    elif len(key_list) == 0:
        mode = "-"
        maxNode = "-"
        bigram_number = "0"

    else:
        mode = key_list[0]
        maxNode = max(new_dict, key=lambda key: new_dict[key])
        bigram_number = str(len(bigrams))

    length_label.config(text=text_length, bg='white', font='verdana 12 bold') #idgfgfjbnberogn
    number_label.config(text=keyword_number, bg='white', font='verdana 12 bold')
    mode_label.config(text=mode, bg='white', font='verdana 12 bold')
    nodes_label.config(text=bigram_number, bg='white', font='verdana 12 bold')
    edges_label.config(text=maxNode, bg='white', font='verdana 12 bold')
    if len(key_list) == 0:
        inderror_label.config(text="Uups..", bg='white', fg='Grey', font='verdana 15 bold')
        error_label.config(text="there are no words that repeat more than " + str(
            count_criteria) + " times. Please chose a lower parameter", bg='white', fg='black', font='verdana 8 bold')
    elif len(key_list) == 1:
        inderror_label.config(text=mode, bg='white', fg='Grey', font='verdana 15 bold')
        error_label.config(text="is the only word that occurs more than " + str(count_criteria) + " times in the text",
                           bg='white', fg='black', font='verdana 8 bold')
    else:
        error_label.lower()
        inderror_label.lower()
        error_label.config(text=None, bg=None, fg='black', font='verdana 8 bold')
        inderror_label.config(text=None, bg=None, fg='Grey', font='verdana 15 bold')

    loading_panel.destroy()

    frm = Frame(root)
    frm.lower()
    panel.lower()
    frm.place(x=210, y=480, anchor='w')

    canvas = FigureCanvasTkAgg(f, master=frm)
    canvas.draw()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.configure(bg="white")
    toolbar.update()
    canvas.tkcanvas.pack()

    if len(key_list) == 0:
        inderror_label.config(text="Uups..", bg='white', fg='Grey', font='verdana 15 bold')
        error_label.config(text="there are no words that repeat more than " + str(
            count_criteria) + " times. Please chose a lower parameter", bg='white', fg='black', font='verdana 8 bold')
    elif len(key_list) == 1:
        inderror_label.config(text=mode, bg='white', fg='Grey', font='verdana 15 bold')
        error_label.config(text="is the only word that occurs more than " + str(count_criteria) + " times in the text",
                           bg='white', fg='black', font='verdana 8 bold')
    else:
        error_label.lower()
        inderror_label.lower()
        error_label.config(text=None, bg=None, fg='black', font='verdana 8 bold')
        inderror_label.config(text=None, bg=None, fg='Grey', font='verdana 15 bold')

    def destroy():

        frm.destroy()
        toolbar.destroy()
        error_label.lower()
        inderror_label.lower()
        length_label.config(text="-")
        number_label.config(text="-")
        nodes_label.config(text="-")
        mode_label.config(text="-")
        edges_label.config(text="-")

    clear_button = Button(root, text="Clear Graph", command=destroy, bg='grey70', relief='flat', cursor='dot')
    clear_button.place(x=20, y=340, anchor='w', height=30, width=210)

    bigram_list = list(coocurences.keys())  # Shows all individual bigrams in descending (count)order
    bigram_counts = list(coocurences.values())  # Shows all individual bigram counts in descending order


textBox = Text(root, height=1, width=70, bg='grey99')
textBox.place(x=540, y=90, anchor='w')
textBox.insert(INSERT, "insert link", 'hint')
textBox.tag_config('hint', foreground="#b3b3b3")


def preset():
    word_count_slider.place(x=20, y=185, anchor='w', width=210)
    slider_set_button.place(x=20, y=260, anchor='w', height=30, width=210)
    expl_label.place(x=20, y=140, anchor='w')
    onCreate_label.place(x=20, y=220, anchor='w')


# This is not tied to anything and is still work in progress
def removepreset():
    try:
        word_count_slider.destroy()
        slider_set_button.destroy()
        expl_label.destroy()
        onCreate_label.destroy()
        pre_count_label.config(text='', bg='grey30')
        suggestion_label.config(text='', bg='grey30')
    finally:
        print('continue')  # Th
# __________________________________________________________

def search():

    global file_label
    global source
    global urlmarker

    loadingsymbol = ImageTk.PhotoImage(Image.open(resource_path("images/new/sand_clock.png")))
    loading_panel = Label(root, image=loadingsymbol, borderwidth=0, compound="none", highlightthickness=0, padx=0,
                          pady=0)
    root.filename = filedialog.askopenfilename(initialdir="/", title="Select A File",
                                               filetypes=(
                                                   ("txt files", "*.txt"), ("pdf files", "*.pdf"),
                                                   ("All Files", "*.*")))
    source = root.filename
    base = os.path.basename(str(root.filename))

    if base:
        loading_panel.place(x=1120, y=60, anchor='w')
        preset()
        input_txt = open(root.filename, "r", encoding="utf8")
        cleanr = re.compile('<.*?>|/&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')  # removing tags from input string
        input_string = re.sub(cleanr, '', input_txt.read())  # tag-cleaned input string
        input_string = input_string.replace('"', '')
        full_string_list = input_string.split()
        file_label.config(text=base, fg='black')
        pre_count_label.config(text='Your text has a length of ' + str(len(full_string_list)) + ' words',
                               bg='grey30', fg='white', font='verdana 8')
        suggestion_label.config(text='Suggested repetition criterion: ' + (str(int(len(full_string_list) * 0.0025))),
                                bg='grey30', fg='white', font='verdana 8')
        urlmarker = 0
        loading_panel.destroy()


def crawl():
    loadingsymbol = ImageTk.PhotoImage(Image.open(resource_path("images/new/sand_clock.png")))
    loading_panel = Label(root, image=loadingsymbol, borderwidth=0, compound="none", highlightthickness=0, padx=0,
                          pady=0)
    loading_panel.place(x=1150, y=60, anchor='w')
    global urlmarker
    global link
    urlmarker = 1

    link = textBox.get("1.0", "end-1c")
    print(link)
    input_string = text_from_html(urlopen(link).read())
    full_string_list = list(input_string.split(" "))
    preset()
    pre_count_label.config(text='Your text has a length of ' + str(len(full_string_list)) + ' words', bg='grey30',
                           fg='white', font='verdana 8')
    suggestion_label.config(text='Suggested repetition criterion: ' + (str(int(len(full_string_list) * 0.0025))),
                            bg='grey30', fg='white', font='verdana 8')
    file_label.config(text='No file selected', bg='white', fg='grey', font='verdana 8')
    loading_panel.destroy()


def trycrawl():
    try:
        crawl()
    except Exception:
        textBox.delete(1.0, END)
        textBox.insert(INSERT, "Nope.. Invalid Link or protected website!!", 'hint')


# place most GUI Assets
img = ImageTk.PhotoImage(Image.open(resource_path("images/sleeping.png")))
panel = Label(root, image=img, borderwidth=0, compound="none", highlightthickness=0, padx=0, pady=0)
panel.place(x=410, y=430, anchor='w')
panel.lower()

vertical_shadow = ImageTk.PhotoImage(Image.open(resource_path("images/Shadowvertical.png")))
vertical_shadow_panel = Label(root, image=vertical_shadow, borderwidth=0, compound="none", highlightthickness=0,
                              padx=0, pady=0)
vertical_shadow_panel.place(x=200, y=200, anchor='w')
vertical_shadow_panel.lower()

horizontal_shadow = ImageTk.PhotoImage(Image.open(resource_path("images/horizontalshadow.png")))
horizontal_shadow_panel = Label(root, image=horizontal_shadow, borderwidth=0, compound="none", highlightthickness=0,
                                padx=0, pady=0)
horizontal_shadow_panel.place(x=360, y=140, anchor='w')
horizontal_shadow_panel.lower()

settingsbg = Canvas(root, height=1500, width=250, bg='grey30', highlightthickness=0)
settingsbg.place(x=0, y=170, anchor='w')

inderror_label = Label(root, text="", bg='white', fg='Grey', font='verdana 15 bold')
inderror_label.place(x=477, y=360, anchor='w')

error_label = Label(root, text="", bg='white', fg='black', font='verdana 8 bold')
error_label.place(x=480, y=400, anchor='w')

analyse_button = Button(root, text='Analyse', command=analysis, bg='grey70', relief='flat', cursor='dot')
pre_count_label = Label(root, text='', bg='grey30', fg='white', font='verdana 8')
pre_count_label.place(x=23, y=90, anchor='w')
suggestion_label = Label(root, text='', bg='grey30', fg='white', font='verdana 8')
suggestion_label.place(x=23, y=115, anchor='w')

# settings_image = ImageTk.PhotoImage(Image.open(resource_path("images/setup_icon.png")))
# settings_panel = Label(root, image=settings_image, borderwidth=0, compound="none", highlightthickness=0,
#                        padx=0, pady=0)
# settings_panel.place(x=70, y=140, anchor='w')
Settings_label = Label(root, text="ANALYSIS SETUP", bg='grey30', fg='white', font='verdana 12 bold')
Settings_label.place(x=43, y=36, anchor='w')

file_image = ImageTk.PhotoImage(Image.open(resource_path("images/doc.png")))
file_panel = Label(root, image=file_image, borderwidth=0, compound="none", highlightthickness=0, padx=0, pady=0)
file_panel.place(x=535, y=36, anchor='w')
file_label = Label(root, text='No file selected', bg='white', fg='grey', font='verdana 8')
file_label.place(x=578, y=36, anchor='w')

url_button = Button(root, text="Set Link", command=trycrawl, bg='grey70', relief='flat', cursor='dot')
url_button.place(x=300, y=90, anchor='w', height=40, width=210)

length_image = ImageTk.PhotoImage(Image.open(resource_path("images/new/Word count.png")))
length_panel = Label(root, image=length_image, borderwidth=0, compound="none", highlightthickness=0, padx=0, pady=0)
length_panel.place(x=300, y=170, anchor='w')
length_sublabel = Label(root, text="Total Word Count", bg='white', fg='grey', font='verdana 8')
length_sublabel.place(x=300, y=200, anchor='w')
length_label = Label(root, text="-", bg='white', font='verdana 12 bold')
length_label.place(x=340, y=170, anchor='w')

number_image = ImageTk.PhotoImage(Image.open(resource_path("images/new/Nodes.png")))
number_panel = Label(root, image=number_image, borderwidth=0, compound="none", highlightthickness=0, padx=0, pady=0)
number_panel.place(x=470, y=170, anchor='w')
number_sublabel = Label(root, text="Number of Nodes", bg='white', fg='grey', font='verdana 8')
number_sublabel.place(x=470, y=200, anchor='w')
number_label = Label(root, text="-", bg='white', font='verdana 12 bold')
number_label.place(x=510, y=170, anchor='w')

nodes_image = ImageTk.PhotoImage(Image.open(resource_path("images/new/Edge count.png")))
nodes_panel = Label(root, image=nodes_image, borderwidth=0, compound="none", highlightthickness=0, padx=0, pady=0)
nodes_panel.place(x=640, y=170, anchor='w')
nodes_sublabel = Label(root, text="Number of Edges", bg='white', fg='grey', font='verdana 8')
nodes_sublabel.place(x=640, y=200, anchor='w')
nodes_label = Label(root, text="-", bg='white', font='verdana 12 bold')
nodes_label.place(x=680, y=170, anchor='w')

mode_image = ImageTk.PhotoImage(Image.open(resource_path("images/new/key node.png")))
mode_panel = Label(root, image=mode_image, borderwidth=0, compound="none", highlightthickness=0, padx=0, pady=0)
mode_panel.place(x=810, y=170, anchor='w')
mode_sublabel = Label(root, text="HOT TOPIC", bg='white', fg='grey', font='verdana 8')
mode_sublabel.place(x=810, y=200, anchor='w')
mode_label = Label(root, text="-", bg='white', font='verdana 12 bold')
mode_label.place(x=850, y=170, anchor='w')

edge_image = ImageTk.PhotoImage(Image.open(resource_path("images/new/Key edge.png")))
edge_panel = Label(root, image=edge_image, borderwidth=0, compound="none", highlightthickness=0, padx=0, pady=0)
edge_panel.place(x=980, y=170, anchor='w')
edge_sublabel = Label(root, text="Key Association", bg='white', fg='grey', font='verdana 8')
edge_sublabel.place(x=980, y=200, anchor='w')
edges_label = Label(root, text="-", bg='white', font='verdana 12 bold')
edges_label.place(x=1040, y=170, anchor='w')

word_count_slider = Scale(root, from_=1, to=200, orient=HORIZONTAL, bg='grey70', relief='flat', cursor='dot')

slider_set_button = Button(root, text='Set', command=slide, bg='grey70', relief='flat', cursor='dot')

expl_label = Label(root, text="Select the minimum repetition criterion", bg='grey30',
                   fg='white', font='verdana 8')

onCreate_label = Label(root, text="No repetition minimum set", bg='grey30',
                       fg='white', font='verdana 8')

open_button = Button(root, text="Open File", command=search, bg='grey70', relief='flat', cursor='dot')
open_button.place(x=300, y=36, anchor='w', height=40, width=210)

go_button = ttk.Button(text="Go", command=close_window)
go_button.place(x=93, y=500, anchor='w', height=30, width=60)
panel.lower()

root.mainloop()
