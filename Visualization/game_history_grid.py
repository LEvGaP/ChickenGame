"""
Scrollable grid view of repeated n-player chicken rounds.

Each row is one round (oldest at top, newest at bottom). Each column is one
player. Cell color encodes the player's move (swerve vs stay) and whether it
matched the mediator recommendation for that player.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import List, Sequence, Tuple

from n_player_chicken_game import STAY, SWERVE

# (action, recommendation_equal) -> fill when action is SWERVE or STAY
_COLOR_SWERVE_FOLLOW = "#0000FF"
_COLOR_SWERVE_DEVIATE = "#FFFF00"
_COLOR_STAY_FOLLOW = "#006400"
_COLOR_STAY_DEVIATE = "#8B0000"


def _cell_color(action: int, recommendation: int) -> str:
    if action == SWERVE:
        return _COLOR_SWERVE_FOLLOW if action == recommendation else _COLOR_SWERVE_DEVIATE
    if action == STAY:
        return _COLOR_STAY_FOLLOW if action == recommendation else _COLOR_STAY_DEVIATE
    raise ValueError(f"action must be SWERVE ({SWERVE}) or STAY ({STAY}), got {action!r}")


class GameHistoryGridView:
    """
    Tkinter window showing round-by-round actions vs mediator recommendations.

    Call :meth:`append_round` after each simulated round, then :meth:`pump`
    (or :meth:`run_mainloop`) so the window stays responsive.
    """

    def __init__(
        self,
        n_players: int,
        *,
        title: str = "Chicken game — moves vs mediator",
        cell_size: int = 22,
    ) -> None:
        if n_players < 1:
            raise ValueError("n_players must be at least 1")
        self._n = n_players
        self._cell = cell_size

        self._root = tk.Tk()
        self._root.title(title)

        self._rounds: List[Tuple[Sequence[int], Sequence[int]]] = []

        outer = ttk.Frame(self._root, padding=4)
        outer.pack(fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(outer, highlightthickness=0, bg="#f5f5f5")
        yscroll = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=yscroll.set)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._inner = ttk.Frame(self._canvas)
        self._win_id = self._canvas.create_window(
            (0, 0), window=self._inner, anchor=tk.NW
        )

        def _on_inner_configure(_event=None) -> None:
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))
            self._scroll_to_bottom()

        def _on_canvas_configure(event) -> None:
            self._canvas.itemconfigure(self._win_id, width=event.width)

        self._inner.bind("<Configure>", _on_inner_configure)
        self._canvas.bind("<Configure>", _on_canvas_configure)

        self._grid_frame = ttk.Frame(self._inner)
        self._grid_frame.pack(fill=tk.BOTH, expand=True)

        corner = ttk.Label(self._grid_frame, text="Round", width=6, anchor=tk.CENTER)
        corner.grid(row=0, column=0, padx=(0, 4), pady=(0, 4))
        for p in range(self._n):
            ttk.Label(
                self._grid_frame,
                text=f"P{p}",
                anchor=tk.CENTER,
                width=4,
            ).grid(row=0, column=p + 1, padx=1, pady=(0, 4))

        legend = ttk.Frame(self._inner)
        legend.pack(fill=tk.X, pady=(8, 0))
        self._build_legend(legend)

        self._cell_widgets: List[List[tk.Canvas]] = []

    def _build_legend(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Legend:").pack(side=tk.LEFT, padx=(0, 8))
        specs = [
            (_COLOR_SWERVE_FOLLOW, "Swerve, followed"),
            (_COLOR_SWERVE_DEVIATE, "Swerve, deviated"),
            (_COLOR_STAY_FOLLOW, "Stay, followed"),
            (_COLOR_STAY_DEVIATE, "Stay, deviated"),
        ]
        for color, text in specs:
            row = ttk.Frame(parent)
            row.pack(side=tk.LEFT, padx=(0, 12))
            sq = tk.Canvas(row, width=14, height=14, highlightthickness=1, highlightbackground="#ccc")
            sq.pack(side=tk.LEFT, padx=(0, 4))
            sq.create_rectangle(1, 1, 13, 13, fill=color, outline="")
            ttk.Label(row, text=text).pack(side=tk.LEFT)

    def append_round(
        self,
        player_moves: Sequence[int],
        mediator_recommendations: Sequence[int],
    ) -> None:
        """
        Append one round to the grid.

        ``player_moves[i]`` and ``mediator_recommendations[i]`` refer to player
        ``i``. Values must be ``SWERVE`` (0) or ``STAY`` (1) from
        :mod:`n_player_chicken_game`.
        """
        if len(player_moves) != self._n or len(mediator_recommendations) != self._n:
            raise ValueError(
                f"expected length {self._n} for both sequences, got "
                f"{len(player_moves)} and {len(mediator_recommendations)}"
            )
        moves = tuple(int(x) for x in player_moves)
        recs = tuple(int(x) for x in mediator_recommendations)
        for i, (a, r) in enumerate(zip(moves, recs)):
            if a not in (SWERVE, STAY) or r not in (SWERVE, STAY):
                raise ValueError(
                    f"player {i}: actions must be SWERVE ({SWERVE}) or STAY ({STAY}), "
                    f"got action={a!r}, recommendation={r!r}"
                )

        self._rounds.append((moves, recs))
        row_index = len(self._rounds) - 1
        grid_row = row_index + 1

        row_cells: List[tk.Canvas] = []
        label = ttk.Label(
            self._grid_frame,
            text=f"R{row_index}",
            width=6,
            anchor=tk.E,
        )
        label.grid(row=grid_row, column=0, padx=(0, 4), pady=1, sticky=tk.E)

        for p in range(self._n):
            c = tk.Canvas(
                self._grid_frame,
                width=self._cell,
                height=self._cell,
                highlightthickness=1,
                highlightbackground="#bbb",
                bg="#eee",
            )
            fill = _cell_color(moves[p], recs[p])
            c.create_rectangle(1, 1, self._cell, self._cell, fill=fill, outline="")
            c.grid(row=grid_row, column=p + 1, padx=1, pady=1)
            row_cells.append(c)
        self._cell_widgets.append(row_cells)

        self._canvas.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._scroll_to_bottom()

    def _scroll_to_bottom(self) -> None:
        self._canvas.yview_moveto(1.0)

    def pump(self) -> None:
        """Process pending UI events without blocking (call from your sim loop)."""
        self._root.update_idletasks()
        self._root.update()

    def run_mainloop(self) -> None:
        """Block and run the Tk event loop until the window is closed."""
        self._root.mainloop()

    def destroy(self) -> None:
        """Close the window."""
        self._root.destroy()

    @property
    def root(self) -> tk.Tk:
        """The underlying Tk root (advanced use: bind keys, embed other widgets)."""
        return self._root
