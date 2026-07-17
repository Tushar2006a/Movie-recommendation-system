import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from io import BytesIO
from PIL import Image, ImageTk

TMDB_API_KEY = "15d2ea6d0dc1d476efbca3eba2b9bbfb"
TMDB_BASE = "https://api.themoviedb.org/3"
IMG_BASE = "https://image.tmdb.org/t/p"

_session = requests.Session()
_retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    raise_on_status=False,
)
_adapter = HTTPAdapter(max_retries=_retry_strategy)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)

COLORS = {
    "bg": "#f5f6f8",
    "card": "#ffffff",
    "text": "#1a1a2e",
    "text_secondary": "#555770",
    "text_muted": "#8b8da3",
    "border": "#e0e2e8",
    "accent": "#2d2d2d",
    "hover": "#ebebeb",
    "rating": "#d4a800",
    "genre_bg": "#f0f1f4",
    "search_bg": "#ffffff",
}

FONT_FAMILY = "Helvetica"


def tmdb_get(endpoint, params=None):
    if params is None:
        params = {}
    params["api_key"] = TMDB_API_KEY
    params["language"] = "en-US"
    time.sleep(0.15)
    response = _session.get(f"{TMDB_BASE}{endpoint}", params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def search_movies(query):
    if not query.strip():
        return []
    data = tmdb_get("/search/movie", {"query": query, "include_adult": "false", "page": "1"})
    return data.get("results", [])


def get_movie_details(movie_id):
    return tmdb_get(f"/movie/{movie_id}")


def get_recommendations(movie_id):
    data = tmdb_get(f"/movie/{movie_id}/recommendations", {"page": "1"})
    return data.get("results", [])


def discover_by_genres(genre_ids, exclude_id):
    if not genre_ids:
        return []
    data = tmdb_get("/discover/movie", {
        "with_genres": ",".join(str(g) for g in genre_ids),
        "sort_by": "vote_average.desc",
        "vote_count.gte": "100",
        "page": "1",
    })
    results = data.get("results", [])
    return [m for m in results if m["id"] != exclude_id]


def load_image_from_url(url, size):
    try:
        resp = _session.get(url, timeout=15)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


class MovieRecommendationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MRS — Movie Recommendation System")
        self.root.geometry("1000x720")
        self.root.minsize(800, 600)
        self.root.configure(bg=COLORS["bg"])

        self._poster_image = None
        self._rec_images = []

        self._search_timer = None

        self._build_header()
        self._build_search()
        self._build_content_area()
        self._build_welcome()

    def _build_header(self):
        header = tk.Frame(self.root, bg=COLORS["card"], height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        inner = tk.Frame(header, bg=COLORS["card"])
        inner.pack(expand=True)

        tk.Label(
            inner, text="MRS", font=(FONT_FAMILY, 18, "bold"),
            bg=COLORS["card"], fg=COLORS["text"]
        ).pack(side="left")

        tk.Label(
            inner, text="  Movie Recommendation System",
            font=(FONT_FAMILY, 10), bg=COLORS["card"], fg=COLORS["text_muted"]
        ).pack(side="left", pady=(4, 0))

        sep = tk.Frame(self.root, bg=COLORS["border"], height=1)
        sep.pack(fill="x", side="top")

    def _build_search(self):
        search_frame = tk.Frame(self.root, bg=COLORS["bg"], pady=20)
        search_frame.pack(fill="x", side="top")

        container = tk.Frame(search_frame, bg=COLORS["bg"])
        container.pack()

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            container,
            textvariable=self.search_var,
            font=(FONT_FAMILY, 13),
            width=45,
            bg=COLORS["search_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
        )
        self.search_entry.pack(side="left", ipady=8, padx=(0, 8))
        self.search_entry.insert(0, "")
        self.search_entry.bind("<Return>", self._on_search_enter)
        self.search_var.trace_add("write", self._on_search_typing)

        search_btn = tk.Button(
            container, text="Search", font=(FONT_FAMILY, 11),
            bg=COLORS["accent"], fg="#ffffff",
            activebackground=COLORS["text_secondary"], activeforeground="#ffffff",
            relief="flat", padx=16, pady=6,
            cursor="hand2",
            command=self._on_search_click,
        )
        search_btn.pack(side="left")

        self.suggestions_frame = tk.Frame(self.root, bg=COLORS["bg"])
        self.suggestions_listbox = tk.Listbox(
            self.suggestions_frame,
            font=(FONT_FAMILY, 11),
            bg=COLORS["card"],
            fg=COLORS["text"],
            selectbackground=COLORS["hover"],
            selectforeground=COLORS["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            height=6,
            activestyle="none",
        )
        self.suggestions_listbox.pack(fill="x", padx=180)
        self.suggestions_listbox.bind("<<ListboxSelect>>", self._on_suggestion_select)
        self.suggestions_listbox.bind("<Double-Button-1>", self._on_suggestion_select)
        self.suggestions_listbox.bind("<Button-1>", self._on_suggestion_click)

        self._suggestion_data = []

        self.root.bind("<Button-1>", self._on_click_outside, add="+")

    def _on_search_typing(self, *args):
        query = self.search_var.get().strip()
        if self._search_timer:
            self.root.after_cancel(self._search_timer)
        if len(query) < 2:
            self._hide_suggestions()
            return
        self._search_timer = self.root.after(400, lambda: self._fetch_suggestions(query))

    def _fetch_suggestions(self, query):
        def worker():
            try:
                results = search_movies(query)[:8]
                self.root.after(0, lambda: self._show_suggestions(results))
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def _show_suggestions(self, movies):
        self._suggestion_data = movies
        self.suggestions_listbox.delete(0, tk.END)
        for m in movies:
            year = m.get("release_date", "")[:4] or "—"
            rating = m.get("vote_average", 0)
            title = m.get("title", "Unknown")
            self.suggestions_listbox.insert(tk.END, f"  {title}  ({year})  ★ {rating:.1f}")
        if movies:
            self.suggestions_frame.pack(fill="x", side="top", before=self.content_canvas)
        else:
            self._hide_suggestions()

    def _hide_suggestions(self):
        self.suggestions_frame.pack_forget()

    def _on_suggestion_click(self, event):
        index = self.suggestions_listbox.nearest(event.y)
        if 0 <= index < len(self._suggestion_data):
            movie = self._suggestion_data[index]
            self.search_var.set(movie["title"])
            self._hide_suggestions()
            self._load_movie(movie["id"])

    def _on_suggestion_select(self, event):
        sel = self.suggestions_listbox.curselection()
        if sel and sel[0] < len(self._suggestion_data):
            movie = self._suggestion_data[sel[0]]
            self.search_var.set(movie["title"])
            self._hide_suggestions()
            self._load_movie(movie["id"])

    def _on_search_enter(self, event):
        self._on_search_click()

    def _on_search_click(self):
        query = self.search_var.get().strip()
        if not query:
            return
        self._hide_suggestions()
        self._show_loading()

        def worker():
            try:
                results = search_movies(query)
                if results:
                    self.root.after(0, lambda: self._load_movie(results[0]["id"]))
                else:
                    self.root.after(0, lambda: messagebox.showinfo("No Results", "No movies found. Try a different search."))
                    self.root.after(0, self._show_welcome)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Search failed:\n{e}"))
                self.root.after(0, self._show_welcome)
        threading.Thread(target=worker, daemon=True).start()

    def _on_click_outside(self, event):
        try:
            clicked = self.root.winfo_containing(event.x_root, event.y_root)
            if clicked == self.suggestions_listbox or clicked == self.search_entry:
                return
            if clicked and str(clicked).startswith(str(self.suggestions_frame)):
                return
        except Exception:
            pass
        self._hide_suggestions()

    def _build_content_area(self):
        self.content_canvas = tk.Canvas(self.root, bg=COLORS["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.content_canvas.yview)

        self.content_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.content_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.content_frame = tk.Frame(self.content_canvas, bg=COLORS["bg"])
        self.content_window = self.content_canvas.create_window(
            (0, 0), window=self.content_frame, anchor="nw"
        )

        self.content_frame.bind("<Configure>", self._on_frame_configure)
        self.content_canvas.bind("<Configure>", self._on_canvas_configure)

        self.content_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_frame_configure(self, event):
        self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.content_canvas.itemconfig(self.content_window, width=event.width)

    def _on_mousewheel(self, event):
        self.content_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_welcome(self):
        self._show_welcome()

    def _show_welcome(self):
        self._clear_content()
        frame = tk.Frame(self.content_frame, bg=COLORS["bg"], pady=80)
        frame.pack(fill="x")

        tk.Label(
            frame, text="🎬", font=(FONT_FAMILY, 40),
            bg=COLORS["bg"]
        ).pack()

        tk.Label(
            frame, text="Find Your Next Favorite Movie",
            font=(FONT_FAMILY, 16, "bold"), bg=COLORS["bg"], fg=COLORS["text"]
        ).pack(pady=(16, 6))

        tk.Label(
            frame,
            text="Search for any movie to see details and get\nrecommendations based on genres and ratings.",
            font=(FONT_FAMILY, 11), bg=COLORS["bg"], fg=COLORS["text_muted"],
            justify="center",
        ).pack()

    def _show_loading(self):
        self._clear_content()
        frame = tk.Frame(self.content_frame, bg=COLORS["bg"], pady=60)
        frame.pack(fill="x")
        tk.Label(
            frame, text="Searching...", font=(FONT_FAMILY, 12),
            bg=COLORS["bg"], fg=COLORS["text_muted"]
        ).pack()

    def _load_movie(self, movie_id):
        self._show_loading()

        def worker():
            try:
                movie = get_movie_details(movie_id)
                recs = get_recommendations(movie_id)

                if len(recs) < 6:
                    genre_ids = [g["id"] for g in movie.get("genres", [])]
                    genre_recs = discover_by_genres(genre_ids, movie_id)
                    existing_ids = {m["id"] for m in recs}
                    for m in genre_recs:
                        if m["id"] not in existing_ids:
                            recs.append(m)
                            existing_ids.add(m["id"])

                recs.sort(
                    key=lambda m: (m.get("vote_average", 0) * 0.7
                                   + min(m.get("popularity", 0) / 100, 3) * 0.3),
                    reverse=True,
                )
                recs = recs[:12]

                poster_path = movie.get("poster_path")
                poster_img = None
                if poster_path:
                    poster_img = load_image_from_url(f"{IMG_BASE}/w342{poster_path}", (200, 300))

                rec_images = []
                for r in recs:
                    rp = r.get("poster_path")
                    if rp:
                        img = load_image_from_url(f"{IMG_BASE}/w185{rp}", (140, 210))
                        rec_images.append(img)
                    else:
                        rec_images.append(None)

                self.root.after(0, lambda: self._render_movie(movie, poster_img, recs, rec_images))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load movie:\n{e}"))
                self.root.after(0, self._show_welcome)

        threading.Thread(target=worker, daemon=True).start()

    def _render_movie(self, movie, poster_img, recs, rec_images):
        self._clear_content()
        self._poster_image = poster_img
        self._rec_images = rec_images

        card = tk.Frame(self.content_frame, bg=COLORS["card"], highlightbackground=COLORS["border"],
                        highlightthickness=1, padx=24, pady=24)
        card.pack(fill="x", padx=24, pady=(8, 0))

        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(fill="x")

        poster_frame = tk.Frame(inner, bg=COLORS["card"])
        poster_frame.pack(side="left", anchor="nw", padx=(0, 24))

        if poster_img:
            poster_label = tk.Label(poster_frame, image=poster_img, bg=COLORS["card"])
            poster_label.pack()
        else:
            placeholder = tk.Label(
                poster_frame, text="No Poster", font=(FONT_FAMILY, 10),
                bg=COLORS["genre_bg"], fg=COLORS["text_muted"],
                width=24, height=14,
            )
            placeholder.pack()

        info_frame = tk.Frame(inner, bg=COLORS["card"])
        info_frame.pack(side="left", fill="both", expand=True, anchor="nw")

        title = movie.get("title", "Unknown")
        tk.Label(
            info_frame, text=title, font=(FONT_FAMILY, 18, "bold"),
            bg=COLORS["card"], fg=COLORS["text"], anchor="w", wraplength=500, justify="left"
        ).pack(fill="x", pady=(0, 8))

        meta_frame = tk.Frame(info_frame, bg=COLORS["card"])
        meta_frame.pack(fill="x", pady=(0, 10))

        year = movie.get("release_date", "")[:4] or "N/A"
        rating = movie.get("vote_average", 0)
        runtime = movie.get("runtime")
        runtime_str = f"{runtime} min" if runtime else "N/A"

        for text in [year, f"★ {rating:.1f}", runtime_str]:
            tag = tk.Label(
                meta_frame, text=f"  {text}  ", font=(FONT_FAMILY, 10),
                bg=COLORS["genre_bg"], fg=COLORS["text_secondary"],
            )
            tag.pack(side="left", padx=(0, 6))

        genres = movie.get("genres", [])
        if genres:
            genre_frame = tk.Frame(info_frame, bg=COLORS["card"])
            genre_frame.pack(fill="x", pady=(0, 12))
            for g in genres:
                tag = tk.Label(
                    genre_frame, text=f"  {g['name']}  ", font=(FONT_FAMILY, 9),
                    bg=COLORS["bg"], fg=COLORS["text_muted"],
                )
                tag.pack(side="left", padx=(0, 4))

        overview = movie.get("overview", "No overview available.")
        tk.Label(
            info_frame, text=overview, font=(FONT_FAMILY, 11),
            bg=COLORS["card"], fg=COLORS["text_secondary"],
            anchor="nw", wraplength=480, justify="left",
        ).pack(fill="x", pady=(0, 14))

        extra_frame = tk.Frame(info_frame, bg=COLORS["card"])
        extra_frame.pack(fill="x")

        lang = (movie.get("original_language") or "—").upper()
        pop = f"{movie.get('popularity', 0):.0f}"
        votes = f"{movie.get('vote_count', 0):,}"

        for label, value in [("Language", lang), ("Popularity", pop), ("Votes", votes)]:
            col = tk.Frame(extra_frame, bg=COLORS["card"])
            col.pack(side="left", padx=(0, 24))
            tk.Label(
                col, text=label.upper(), font=(FONT_FAMILY, 8, "bold"),
                bg=COLORS["card"], fg=COLORS["text_muted"],
            ).pack(anchor="w")
            tk.Label(
                col, text=value, font=(FONT_FAMILY, 11, "bold"),
                bg=COLORS["card"], fg=COLORS["text"],
            ).pack(anchor="w")

        if recs:
            rec_section = tk.Frame(self.content_frame, bg=COLORS["bg"])
            rec_section.pack(fill="x", padx=24, pady=(28, 8))

            tk.Label(
                rec_section, text="Similar Movies You Might Like",
                font=(FONT_FAMILY, 14, "bold"), bg=COLORS["bg"], fg=COLORS["text"],
                anchor="w",
            ).pack(fill="x", pady=(0, 14))

            grid = tk.Frame(rec_section, bg=COLORS["bg"])
            grid.pack(fill="x")

            cols = 5
            for i, rec_movie in enumerate(recs):
                row = i // cols
                col = i % cols

                card_frame = tk.Frame(grid, bg=COLORS["card"], highlightbackground=COLORS["border"],
                                      highlightthickness=1, cursor="hand2")
                card_frame.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

                grid.columnconfigure(col, weight=1)

                rec_img = rec_images[i] if i < len(rec_images) else None
                if rec_img:
                    img_label = tk.Label(card_frame, image=rec_img, bg=COLORS["card"])
                    img_label.pack(padx=4, pady=(4, 0))
                else:
                    img_label = tk.Label(
                        card_frame, text="No Poster", font=(FONT_FAMILY, 8),
                        bg=COLORS["genre_bg"], fg=COLORS["text_muted"],
                        width=18, height=10,
                    )
                    img_label.pack(padx=4, pady=(4, 0))

                rec_title = rec_movie.get("title", "Unknown")
                tk.Label(
                    card_frame, text=rec_title, font=(FONT_FAMILY, 9, "bold"),
                    bg=COLORS["card"], fg=COLORS["text"],
                    wraplength=130, anchor="w",
                ).pack(fill="x", padx=6, pady=(6, 2))

                rec_year = rec_movie.get("release_date", "")[:4] or "—"
                rec_rating = rec_movie.get("vote_average", 0)
                meta_label = tk.Label(
                    card_frame, text=f"{rec_year}  ★ {rec_rating:.1f}",
                    font=(FONT_FAMILY, 8), bg=COLORS["card"], fg=COLORS["text_muted"],
                    anchor="w",
                )
                meta_label.pack(fill="x", padx=6, pady=(0, 8))

                mid = rec_movie["id"]
                for widget in [card_frame, meta_label, img_label if rec_img else None]:
                    if widget:
                        widget.bind("<Button-1>", lambda e, m=mid: self._on_rec_click(m))

            tk.Frame(self.content_frame, bg=COLORS["bg"], height=40).pack(fill="x")

        self.content_canvas.yview_moveto(0)

    def _on_rec_click(self, movie_id):
        self._load_movie(movie_id)

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()

    style = ttk.Style()
    available_themes = style.theme_names()
    if "aqua" in available_themes:
        style.theme_use("aqua")
    elif "clam" in available_themes:
        style.theme_use("clam")

    app = MovieRecommendationApp(root)
    root.mainloop()
