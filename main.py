import tkinter as tk
import customtkinter
import os
from tkinter import messagebox
from tkinter import *
from PIL import ImageTk, Image
import pyglet #to add fonts
import pandas as pd
import re #regular expression library
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np 

bg_color = "#222222" #setting a background color to be used throughout
pyglet.font.add_file("fonts/Ubuntu-Bold.ttf")  #adding fonts
pyglet.font.add_file("fonts/Shanti-Regular.ttf")

customtkinter.set_appearance_mode("dark")  #setting a theme
customtkinter.set_default_color_theme("dark-blue")


#function to clear widgets when switiching windows
def clear_widgets(frame):
    # select all frame widgets and delete them
    for widget in frame.winfo_children():
        widget.destroy()


#clearing the search engine after an entry
def clear_searchbox():
    searchbox_entry.delete(0, END)


root = customtkinter.CTk()
root.title("MovEngine")
root.config(bg=bg_color)

# creating a frame widget for all windows
global front_window
front_window = tk.Frame(root, width=800, height=600, bg=bg_color)
global registration_window
registration_window = tk.Frame(root, width=800, height=600, bg=bg_color)
global second_window
second_window = tk.Frame(root, width=800, height=600, bg=bg_color)
global watchlist_window
watchlist_window = tk.Frame(root, width=800, height=600, bg=bg_color)
global history_window
history_window = tk.Frame(root, width=800, height=600, bg=bg_color)

frame_list = [front_window, registration_window, second_window, watchlist_window, history_window]

#displaying the windows
for frame in (frame_list):
    frame.grid(row=0, column=0, sticky="nesw")


#reading in the database files
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")


watchlist_queue_list = [] #queue for watchlist (gui)
search_history_stack = [] #stack for history (gui)

#node class
class Node:

    def __init__(self, data):
        self.data = data
        self.next = None

#watchlist class (queue)
class Watchlist_Queue:

    #front stores front node
    def __init__(self):
        self.front = self.rear = None


    def isEmpty(self):
        return self.front == None

    # Method to add an item to the queue
    def enqueue(self, item):
        temp = Node(item)
        watchlist_queue_list.append(item)

        if self.rear == None:
            self.front = self.rear = temp
            return
        self.rear.next = temp
        self.rear = temp

    # Method to remove an item from queue
    def dequeue(self):

        if self.isEmpty():
            return

        temp = self.front
        self.front = temp.next
        watchlist_queue_list.pop(0)
        watchlist_box.delete(0)

        if (self.front == None):
            self.rear = None


q = Watchlist_Queue()

#function to add movies to watchlist using buttons
class addbutton_cmd:

    def addfirst(self):
        q.enqueue(recommended_movies_title[0])

    def addsecond(self):
        q.enqueue(recommended_movies_title[1])

    def addthird(self):
        q.enqueue(recommended_movies_title[2])

    def addfourth(self):
        q.enqueue(recommended_movies_title[3])

    def addfifth(self):
        q.enqueue(recommended_movies_title[4])

    def addsixth(self):
        q.enqueue(recommended_movies_title[5])

    def addseventh(self):
        q.enqueue(recommended_movies_title[6])

    def addeigth(self):
        q.enqueue(recommended_movies_title[7])

    def addninth(self):
        q.enqueue(recommended_movies_title[8])

    def addtenth(self):
        q.enqueue(recommended_movies_title[9])


add_obj = addbutton_cmd()


#class to add search history (stack)
class SearchHistoryStack:

    def __init__(self):
        self.head = None

    def isempty(self):
        if self.head == None:
            return True
        else:
            return False

    def push(self, data):

        if self.head == None:
            self.head = Node(data)
            search_history_stack.append(data)
        else:
            newnode = Node(data)
            newnode.next = self.head
            self.head = newnode
            search_history_stack.append(data)

    def pop(self):

        if self.isempty():
            return None
        else:
            poppednode = self.head
            self.head = self.head.next
            poppednode.next = None
            search_history_stack.pop()
            search_history_box.delete(0)
            return poppednode.data


    def display(self):

        iternode = self.head
        if self.isempty():
            print("Stack Underflow")

        else:
            while (iternode != None):
                print(iternode.data, end="")
                iternode = iternode.next
                if (iternode != None):
                    print(" -> ", end="")
            return


s = SearchHistoryStack()

#function to clean the movie title (extra characters that make search difficult)
def clean_title(title):

    #re.sub() removes characters that we don't want
    return re.sub("[^a-zA-Z0-9 ]", "", str(title))


#applying the clean title function to title column to make new column with cleaned up titles
movies["clean_title"] = movies["title"].apply(clean_title)

#building a tfidf matrix to make search better
#term frequency matrix shows how many times a word occurs in the title
#idf matrix helps the search engine find terms that are unique
#tfidf matrix gives a vector that we compare with the search term and returns result based on vector similarity

vectorizer = TfidfVectorizer(ngram_range=(1, 2)) #ngram range looks at two consecutive words in the title to make search accurate

tfidf = vectorizer.fit_transform(movies["clean_title"]) #turning set of titles into a matrix/vector


def search_title(title):

    title = clean_title(title)
    query_vec = vectorizer.transform([title]) #turning search term to vector

    similarity = cosine_similarity(query_vec, tfidf).flatten() #finding similarity between search term and movies in database using cosine similarity

    indices = np.argpartition(similarity, -5)[-5:] #finding the 5 most similar titles to search term in the database

    results = movies.iloc[indices][::-1] #getting the index of the similar movies in the database

    return results

#collaborative filtering function
def find_similar_movies(movie_id):

    #find the users who watched and also liked the same movie and rated above 4
    similar_users = ratings[(ratings["movieId"] == movie_id) & (ratings["rating"] > 4)]["userId"].unique() #only taking unique user id's

    #finding other movies those same users liked
    similar_user_recs = ratings[(ratings["userId"].isin(similar_users)) & (ratings["rating"] > 4)]["movieId"]

    #finding only those movies that users that are similar to us by more than 10% liked
    similar_user_recs = similar_user_recs.value_counts() / len(similar_users) #value counts gives how many times the movie has been rated
    similar_user_recs = similar_user_recs[similar_user_recs > .10]


    #finding how much all of the users in the dataset like these movies

    #finding all the users that have rated the movies that are the in the similar recs and by more than 4
    all_users = ratings[(ratings["movieId"].isin(similar_user_recs.index)) & (ratings["rating"] > 4)]

    #finding what percentage of all users recommend each of these movies
    all_user_recs = all_users["movieId"].value_counts() / len(all_users["userId"].unique())

    #comparing the percentages
    rec_percentages = pd.concat([similar_user_recs, all_user_recs], axis=1) #concat combines the two series together
    rec_percentages.columns = ["similar", "all"]

    #creating a similarity score by dividing the percentages of how much users similar to us liked the movie by all users
    rec_percentages["score"] = rec_percentages["similar"] / rec_percentages["all"]

    #sorting the scores by biggest
    rec_percentages = rec_percentages.sort_values("score", ascending=False)

    #taking top 10 recs and merging it with movies data so we can access titles
    global display_recs
    display_recs = rec_percentages.head(10).merge(movies, left_index=True, right_on="movieId")[["score", "title"]]

    global recommended_movies_score
    recommended_movies_score = display_recs["score"].tolist()

    global recommended_movies_title
    recommended_movies_title = display_recs["title"].tolist()


#searching the movie from database and recommending titles
def search_movie():

    s.push(search_entry.get())
    movies_result = search_title(search_entry.get())
    movie_id = movies_result.iloc[0]["movieId"] #extracting movie id of the searched title
    find_similar_movies(movie_id) #running recommendation function on the title


#function to display the search results on the window
def display_results_on_screen():

    global score_txt
    score_txt = tk.Label(
        second_window,
        text="Similarity",
        bg=bg_color,
        fg="white",
        font=("Shanti", 16),
    )
    score_txt.place(x=50, y=180)

    global title_txt
    title_txt = tk.Label(
        second_window,
        text="Movie",
        bg=bg_color,
        fg="white",
        font=("Shanti", 16),
    )
    title_txt.place(x=170, y=180)

    global score_list
    score_list = Listbox(second_window,
                         bg=bg_color,
                         fg="white",
                         font=("Shanti", 16),
                         relief=GROOVE,
                         width=8
                         )

    #adding similarity scores to listbox widget to display on screen
    if len(recommended_movies_score) == 0:
        pass
    else:
        for i in recommended_movies_score:
            score_list.insert(END, str(i) + "\n \n")
            score_list.place(x=55, y=240)

    #adding movie recommendations to listbox widget to display on screen
    global recs_list
    recs_list = Listbox(second_window,
                        bg=bg_color,
                        fg="white",
                        font=("Shanti", 16),
                        relief=GROOVE,
                        width=0
                        )

    #if movie is not present in the database
    if len(recommended_movies_title) == 0:
        item = messagebox.showerror("Error!", "Movie not found!")
        if item:
            clear_add_buttons()
    else:
        #if movie is present in the database, add to recommmendation list
        for i in recommended_movies_title:
            recs_list.insert(END, str(i) + "\n \n")
            recs_list.place(x=175, y=240)


#function to display add buttons on screen
def add_to_watchlist_buttons():
    global add1
    add1 = tk.Button(
        second_window,
        text="Add",
        font=("Ubuntu", 9),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [add_obj.addfirst()],
    )
    add1.place(x=700, y=240)

    global add2
    add2 = tk.Button(
        second_window,
        text="Add",
        font=("Ubuntu", 9),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [add_obj.addsecond()],
    )
    add2.place(x=700, y=265)

    global add3
    add3 = tk.Button(
        second_window,
        text="Add",
        font=("Ubuntu", 9),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [add_obj.addthird()],
    )
    add3.place(x=700, y=290)

    global add4
    add4 = tk.Button(
        second_window,
        text="Add",
        font=("Ubuntu", 9),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [add_obj.addfourth()],
    )
    add4.place(x=700, y=315)

    global add5
    add5 = tk.Button(
        second_window,
        text="Add",
        font=("Ubuntu", 9),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [add_obj.addfifth()],
    )
    add5.place(x=700, y=340)

    global add6
    add6 = tk.Button(
        second_window,
        text="Add",
        font=("Ubuntu", 9),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [add_obj.addsixth()],
    )
    add6.place(x=700, y=365)

    global add7
    add7 = tk.Button(
        second_window,
        text="Add",
        font=("Ubuntu", 9),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [add_obj.addseventh()],
    )
    add7.place(x=700, y=390)

    global add8
    add8 = tk.Button(
        second_window,
        text="Add",
        font=("Ubuntu", 9),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [add_obj.addeigth()],
    )
    add8.place(x=700, y=415)

    global add9
    add9 = tk.Button(
        second_window,
        text="Add",
        font=("Ubuntu", 9),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [add_obj.addninth()],
    )
    add9.place(x=700, y=440)

    global add10
    add10 = tk.Button(
        second_window,
        text="Add",
        font=("Ubuntu", 9),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [add_obj.addtenth()],
    )
    add10.place(x=700, y=465)


#function to clear add buttons after a search
def clear_add_buttons():
    score_txt.destroy()
    title_txt.destroy()
    add1.destroy()
    add2.destroy()
    add3.destroy()
    add4.destroy()
    add5.destroy()
    add6.destroy()
    add7.destroy()
    add8.destroy()
    add9.destroy()
    add10.destroy()


#taking the user's data when they register and storing it in the directory for future use
def register_user():
    username_info = username_entry3.get()
    password_info = password_entry3.get()
    name_info = name_entry3.get()
    email_info = email_entry3.get()

    user_data = open(username_info, "w")
    user_data.write(username_info + "\n")
    user_data.write(password_info + "\n")
    user_data.write(name_info + "\n")
    user_data.write(email_info + "\n")
    user_data.close()

    username_entry2.delete(0, END)
    password_entry2.delete(0, END)
    name_entry2.delete(0, END)
    email_entry2.delete(0, END)

    messagebox.showinfo("Success!", "Your account has been successfully created!")

#verifying login data
def login_verify():
    username1 = username_verify.get()
    password1 = password_verify.get()
    username_entry.delete(0, END)
    password_entry.delete(0, END)

    list_of_files = os.listdir()
    #if the user is registered and log-in data is present, user can log-in to the program
    if username1 in list_of_files:
        file1 = open(username1, "r")
        verify = file1.read().splitlines()
        if password1 in verify:
            messagebox.showinfo("Success!", "You have been successfully logged in!")
            load_secondwindow()
        else:
            messagebox.showerror("Error!", "Password not found!") #error if wrong password entered
    else:
        messagebox.showerror("User not found!", "User does not exist!") #error if not registered


#function to display the main window
def load_frontwindow():

    front_window.tkraise() #switching between frames
    front_window.pack_propagate(False)

    #importing logo
    logo_img = ImageTk.PhotoImage(file="images/MovEngine-1.png")
    logo_widget = tk.Label(front_window, image=logo_img, bg=bg_color)
    logo_widget.image = logo_img
    logo_widget.pack()

    # text widget
    username_txt = tk.Label(
        front_window,
        text="Username",
        bg=bg_color,
        fg="white",
        font=("Shanti", 14),
    ).place(x=220, y=250)
    #taking username entry
    global username_verify
    username_verify = StringVar()
    global username_entry
    username_entry = tk.Entry(front_window, font=("Shanti", 16), textvariable=username_verify)
    username_entry.place(x=325, y=250)

    password_txt = tk.Label(
        front_window,
        text="Password",
        bg=bg_color,
        fg="white",
        font=("Shanti", 14),
    ).place(x=220, y=300)
    #taking password entry
    global password_verify
    password_verify = StringVar()
    global password_entry
    password_entry = tk.Entry(front_window, font=("Shanti", 16), show="*", textvariable=password_verify)
    password_entry.place(x=325, y=300)

    register_txt = tk.Label(
        front_window,
        text="Don't have an account?",
        bg=bg_color,
        fg="white",
        font=("Shanti", 14),
    ).place(x=298, y=410)

    #login button
    login_button = tk.Button(
        front_window,
        text="Log-in",
        font=("Ubuntu-Bold", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: login_verify(), #verifies login
    ).pack(pady=95)

    #register button
    register_button = tk.Button(
        front_window,
        text="Register",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: load_registrationwindow(), #loads registration window
    ).place(x=356, y=450)

    #exit button
    exit_button = tk.Button(
        front_window,
        text="Exit Application",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: root.destroy(), #exits program
    ).place(x=326, y=500)


#function to display the search engine window
def load_secondwindow():

    #clears widgets when switiching from different frames
    clear_widgets(front_window)
    clear_widgets(watchlist_window)
    clear_widgets(history_window)
    second_window.tkraise()

    #importing logo
    logo_img = ImageTk.PhotoImage(file="images/MovEngine-2.png")
    logo_widget = tk.Label(second_window, image=logo_img, bg=bg_color)
    logo_widget.image = logo_img
    logo_widget.pack()


    global searchbox_txt
    searchbox_txt = tk.Label(
        second_window,
        text="Enter Movie Name: ",
        bg=bg_color,
        fg="white",
        font=("Shanti", 14),
    ).place(x=150, y=120)

    #search engine widget
    global search_entry
    search_entry = StringVar()
    global searchbox_entry
    searchbox_entry = tk.Entry(second_window, font=("Shanti", 16), textvariable=search_entry)
    searchbox_entry.place(x=320, y=120)

    #search button
    search_button = tk.Button(
        second_window,
        text="Search",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [search_movie(), clear_searchbox(), display_results_on_screen(), add_to_watchlist_buttons()] #searches for movies, clears search engine, displays results, displays add buttons
    ).place(x=580, y=112)

    #clearing search engine
    clear_button = tk.Button(
        second_window,
        text="Clear",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [recs_list.destroy(), score_list.destroy(), clear_add_buttons()] #destroys previous entries in the recommmendation listbox widget in the gui
    ).place(x=660, y=112)

    #watchlist button
    watchlist_button = tk.Button(
        second_window,
        text="Watchlist",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [load_watchlistwindow()] #loads watchlist window
    ).place(x=5, y=5)

    #search history button
    to_search_history = tk.Button(
        second_window,
        text="Search History",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: load_historywindow() #loads history window
    ).place(x=5, y=50)

    #logot button
    logout_button = tk.Button(
        second_window,
        text="Log Out",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: load_frontwindow(), #takes you to main menu
    ).place(x=710, y=5)


#function to display watchlist window on screen
def load_watchlistwindow():

    #clearing widgets of other frames
    clear_widgets(second_window)
    clear_widgets(history_window)
    watchlist_window.tkraise()

    #importing logo
    logo_img = ImageTk.PhotoImage(file="images/MovEngine-2.png")
    logo_widget = tk.Label(watchlist_window, image=logo_img, bg=bg_color)
    logo_widget.image = logo_img
    logo_widget.pack()


    watchlist_title_txt = tk.Label(
        watchlist_window,
        text="Your Personal Watchlist",
        bg=bg_color,
        fg="white",
        font=("Shanti", 17),
    ).place(x=270, y=120)

    #gui listbox in which waatchlist entries are stored
    global watchlist_box
    watchlist_box = Listbox(watchlist_window,
                            bg=bg_color,
                            fg="white",
                            font=("Shanti", 15),
                            relief=GROOVE,
                            width=0
                            )

    if len(watchlist_queue_list) == 0:
        pass
    else:
        #adds entries in the gui and displays it on screen
        for i in watchlist_queue_list:
            watchlist_box.insert(END, str(i) + "\n \n")
            watchlist_box.pack(pady=110)

    #removes entries from watchlist
    dequeue_watchlist = tk.Button(
        watchlist_window,
        text="Remove",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: update_watchlist(),
    ).place(x=710, y=9)

    #loads search engine window
    back_to_search_engine = tk.Button(
        watchlist_window,
        text="Search Engine",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: load_secondwindow(),
    ).place(x=5, y=5)

    #loads search history window
    to_search_history = tk.Button(
        watchlist_window,
        text="Search History",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: load_historywindow()
    ).place(x=5, y=50)


#function to dequeue entries from watchlist queue
def update_watchlist():

    if len(watchlist_queue_list) > 0:
        q.dequeue()
        watchlist_box.pack()
    elif len(watchlist_queue_list) == 0:
        watchlist_box.destroy()
        messagebox.showerror("Error!", "Your watchlist is empty!")

#functions to pop entries from search history stack
def updatesearch_history():

    if len(search_history_stack) > 0:
        s.pop()
        search_history_box.pack()
    elif len(search_history_stack) == 0:
        search_history_box.destroy()
        messagebox.showerror("Error!", "Your search history is empty!")


def load_historywindow():

    clear_widgets(second_window)
    clear_widgets(watchlist_window)

    history_window.tkraise()

    logo_img = ImageTk.PhotoImage(file="images/MovEngine-2.png")
    logo_widget = tk.Label(history_window, image=logo_img, bg=bg_color)
    logo_widget.image = logo_img
    logo_widget.pack()

    history_title_txt = tk.Label(
        history_window,
        text="Your Search History",
        bg=bg_color,
        fg="white",
        font=("Shanti", 17),
    ).place(x=295, y=120)

    #gui listbox to display search history
    global search_history_box
    search_history_box = Listbox(history_window,
                                 bg=bg_color,
                                 fg="white",
                                 font=("Shanti", 15),
                                 relief=GROOVE,
                                 width=0
                                 )

    if len(search_history_stack) == 0:
        pass
    else:
        for i in search_history_stack:
            search_history_box.insert(0, str(i) + "\n \n")
            search_history_box.pack(pady=110)

    #loads watchlist window
    watchlist_button = tk.Button(
        history_window,
        text="Watchlist",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [load_watchlistwindow()]
    ).place(x=5, y=5)

    #loads search engine window
    to_search_engine = tk.Button(
        history_window,
        text="Search Engine",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: load_secondwindow()
    ).place(x=5, y=50)

    #delete search history button
    pop_searchhistory = tk.Button(
        history_window,
        text="Delete",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: updatesearch_history(),
    ).place(x=702, y=5)

#function to load registration window
def load_registrationwindow():

    clear_widgets(front_window)
    registration_window.tkraise()

    logo_img = ImageTk.PhotoImage(file="images/MovEngine-1.png")
    logo_widget = tk.Label(registration_window, image=logo_img, bg=bg_color)
    logo_widget.image = logo_img
    logo_widget.place(x=247, y=1)

    newaccount_txt = tk.Label(
        registration_window,
        text="Create a new account",
        bg=bg_color,
        fg="white",
        font=("Shanti", 14),
    ).place(x=300, y=215)

    #name entry
    name_txt = tk.Label(
        registration_window,
        text="Enter name: ",
        bg=bg_color,
        fg="white",
        font=("Shanti", 14),
    ).place(x=220, y=270)

    global name_entry3
    name_entry3 = StringVar()
    global name_entry2
    name_entry2 = tk.Entry(registration_window, font=("Shanti", 16), textvariable=name_entry3)
    name_entry2.place(x=340, y=270)

    #email entry
    email_txt = tk.Label(
        registration_window,
        text="Enter e-mail: ",
        bg=bg_color,
        fg="white",
        font=("Shanti", 14),
    ).place(x=220, y=320)

    global email_entry3
    email_entry3 = StringVar()
    global email_entry2
    email_entry2 = tk.Entry(registration_window, font=("Shanti", 16), textvariable=email_entry3)
    email_entry2.place(x=340, y=320)

    #username entry
    username_txt = tk.Label(
        registration_window,
        text="Enter username: ",
        bg=bg_color,
        fg="white",
        font=("Shanti", 11),
    ).place(x=220, y=370)

    global username_entry3
    username_entry3 = StringVar()
    global username_entry2
    username_entry2 = tk.Entry(registration_window, font=("Shanti", 16), textvariable=username_entry3)
    username_entry2.place(x=340, y=370)

    #password entry
    password_txt = tk.Label(
        registration_window,
        text="Enter password: ",
        bg=bg_color,
        fg="white",
        font=("Shanti", 11),
    ).place(x=220, y=420)

    global password_entry3
    password_entry3 = StringVar()
    global password_entry2
    password_entry2 = tk.Entry(registration_window, font=("Shanti", 16), textvariable=password_entry3)
    password_entry2.place(x=340, y=420)

    #button to create account
    createacc_button = tk.Button(
        registration_window,
        text="Create account",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: [register_user(), load_frontwindow()],
    ).place(x=330, y=470)

    #button to load main menu
    back_button = tk.Button(
        registration_window,
        text="Back",
        font=("Ubuntu", 15),
        bg="#D6D6D6",
        fg="black",
        cursor="hand2",
        activebackground="#badee2",
        activeforeground="black",
        command=lambda: load_frontwindow(),
    ).place(x=367, y=520)


load_frontwindow()

root.mainloop() #running the application