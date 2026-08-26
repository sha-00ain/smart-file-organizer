from pathlib import Path
import json


# ============================================================
# SETTINGS
# ============================================================

CATEGORIES_FILE = Path(__file__).parent / "categories.json"


# ============================================================
# DEFAULT CATEGORIES
# ============================================================

DEFAULT_CATEGORIES = {

    "Images": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".svg",
        ".ico",
        ".tiff",
    ],

    "Videos": [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
    ],

    "Audio": [
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".m4a",
        ".wma",
    ],

    "Documents": [
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
        ".ppt",
        ".pptx",
        ".xls",
        ".xlsx",
        ".csv",
    ],

    "Archives": [
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".tgz",
        ".bz2",
    ],

    "Programs": [
        ".exe",
        ".msi",
        ".apk",
        ".deb",
        ".dmg",
        ".iso",
    ],

    "Others": [],
}


# ============================================================
# LOAD CATEGORIES
# ============================================================

def load_categories():

    # If categories.json doesn't exist,
    # create it using default categories.

    if not CATEGORIES_FILE.exists():

        save_categories(
            DEFAULT_CATEGORIES
        )

        return {
            key: value.copy()
            for key, value in DEFAULT_CATEGORIES.items()
        }


    try:

        with open(
            CATEGORIES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)


        # Make sure Others always exists

        if "Others" not in data:

            data["Others"] = []


        return data


    except (
        json.JSONDecodeError,
        OSError
    ):

        return {
            key: value.copy()
            for key, value in DEFAULT_CATEGORIES.items()
        }


# ============================================================
# SAVE CATEGORIES
# ============================================================

def save_categories(categories):

    try:

        with open(
            CATEGORIES_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                categories,
                file,
                indent=4
            )


    except OSError as error:

        print(
            f"Could not save categories: {error}"
        )


# ============================================================
# GLOBAL CATEGORIES
# ============================================================

CATEGORIES = load_categories()


# ============================================================
# FIND CATEGORY
# ============================================================

def get_category(file_path):

    extension = file_path.suffix.lower()


    for category, extensions in CATEGORIES.items():

        if extension in extensions:

            return category


    return "Others"


# ============================================================
# CREATE UNIQUE DESTINATION
# ============================================================

def get_unique_destination(destination):

    """
    If destination already exists:

        photo.jpg
        photo (1).jpg
        photo (2).jpg

    This prevents overwriting existing files.
    """

    if not destination.exists():

        return destination


    parent = destination.parent

    stem = destination.stem

    suffix = destination.suffix


    counter = 1


    while True:

        new_name = (
            f"{stem} ({counter}){suffix}"
        )

        new_destination = (
            parent / new_name
        )


        if not new_destination.exists():

            return new_destination


        counter += 1


# ============================================================
# ORGANIZE FILES
# ============================================================

def organize_files(
    folder,
    dry_run=False
):

    """
    Organize files inside a folder.

    Returns:

        results
        moved_files
    """


    folder = Path(folder)


    results = []

    moved_files = []


    # --------------------------------------------------------
    # VALIDATE FOLDER
    # --------------------------------------------------------

    if not folder.exists():

        results.append(
            f"Folder does not exist: {folder}"
        )

        return results, moved_files


    if not folder.is_dir():

        results.append(
            f"Not a folder: {folder}"
        )

        return results, moved_files


    # --------------------------------------------------------
    # FIND FILES
    # --------------------------------------------------------

    files = [

        item

        for item in folder.iterdir()

        if item.is_file()

    ]


    # --------------------------------------------------------
    # NO FILES
    # --------------------------------------------------------

    if not files:

        return results, moved_files


    # --------------------------------------------------------
    # ORGANIZE EACH FILE
    # --------------------------------------------------------

    for file_path in sorted(
        files,
        key=lambda item: item.name.lower()
    ):


        # ----------------------------------------------------
        # CATEGORY
        # ----------------------------------------------------

        category = get_category(
            file_path
        )


        # ----------------------------------------------------
        # DESTINATION FOLDER
        # ----------------------------------------------------

        category_folder = (
            folder / category
        )


        destination = (
            category_folder / file_path.name
        )


        # ----------------------------------------------------
        # AVOID MOVING INTO ITSELF
        # ----------------------------------------------------

        if destination == file_path:

            continue


        # ----------------------------------------------------
        # UNIQUE NAME
        # ----------------------------------------------------

        final_destination = (
            get_unique_destination(
                destination
            )
        )


        # ----------------------------------------------------
        # PREVIEW MODE
        # ----------------------------------------------------

        if dry_run:

            results.append(
                f"[PREVIEW] {file_path.name}\n"
                f"  Category: {category}\n"
                f"  Would move to: "
                f"{final_destination}"
            )

            continue


        # ----------------------------------------------------
        # CREATE CATEGORY FOLDER
        # ----------------------------------------------------

        try:

            category_folder.mkdir(
                parents=True,
                exist_ok=True
            )


        except OSError as error:

            results.append(
                f"[ERROR] Could not create "
                f"{category} folder for "
                f"{file_path.name}\n"
                f"  {error}"
            )

            continue


        # ----------------------------------------------------
        # MOVE FILE
        # ----------------------------------------------------

        try:

            file_path.rename(
                final_destination
            )


            # Save original and new location
            # for Undo.

            moved_files.append(
                (
                    str(final_destination),
                    str(file_path)
                )
            )


            results.append(
                f"[MOVED] {file_path.name}\n"
                f"  Category: {category}\n"
                f"  → {final_destination}"
            )


        except OSError as error:

            results.append(
                f"[ERROR] Could not move "
                f"{file_path.name}\n"
                f"  {error}"
            )


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    if not dry_run and moved_files:

        summary = build_summary(
            moved_files
        )


        if summary:

            results.append(
                "\n" + summary
            )


    return results, moved_files


# ============================================================
# BUILD SUMMARY
# ============================================================

def build_summary(
    moved_files
):

    """
    Create category-wise summary.

    Example:

        Summary
        -------
        Images: 4
        Documents: 3
        Videos: 2
    """


    counts = {}


    for new_path, old_path in moved_files:

        new_path = Path(
            new_path
        )


        category = (
            new_path.parent.name
        )


        counts[category] = (
            counts.get(category, 0) + 1
        )


    if not counts:

        return ""


    lines = [
        "Summary",
        "-------"
    ]


    for category in sorted(
        counts
    ):

        lines.append(
            f"{category}: {counts[category]}"
        )


    lines.append(
        f"Total: {len(moved_files)}"
    )


    return "\n".join(
        lines
    )


# ============================================================
# UNDO MOVES
# ============================================================

def undo_moves(
    moved_files
):

    """
    Restore files to their original locations.
    """


    results = []


    if not moved_files:

        return results


    # Reverse order is safer
    # when multiple files are involved.

    for new_path, old_path in reversed(
        moved_files
    ):

        new_path = Path(
            new_path
        )

        old_path = Path(
            old_path
        )


        # ----------------------------------------------------
        # FILE NO LONGER EXISTS
        # ----------------------------------------------------

        if not new_path.exists():

            results.append(
                f"[ERROR] File not found:\n"
                f"  {new_path}"
            )

            continue


        # ----------------------------------------------------
        # ORIGINAL LOCATION EXISTS
        # ----------------------------------------------------

        final_old_path = (
            get_unique_destination(
                old_path
            )
        )


        try:

            final_old_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )


            new_path.rename(
                final_old_path
            )


            results.append(
                f"[RESTORED] "
                f"{new_path.name}\n"
                f"  → {final_old_path}"
            )


        except OSError as error:

            results.append(
                f"[ERROR] Could not restore "
                f"{new_path.name}\n"
                f"  {error}"
            )


    # --------------------------------------------------------
    # REMOVE EMPTY CATEGORY FOLDERS
    # --------------------------------------------------------

    cleanup_empty_folders(
        moved_files
    )


    return results


# ============================================================
# CLEAN EMPTY CATEGORY FOLDERS
# ============================================================

def cleanup_empty_folders(
    moved_files
):

    """
    Remove empty category folders after Undo.
    """


    checked = set()


    for new_path, _ in moved_files:

        new_path = Path(
            new_path
        )


        category_folder = (
            new_path.parent
        )


        if category_folder in checked:

            continue


        checked.add(
            category_folder
        )


        if not category_folder.exists():

            continue


        try:

            if not any(
                category_folder.iterdir()
            ):

                category_folder.rmdir()


        except OSError:

            # Ignore cleanup errors.
            pass


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print(
        "Smart File Organizer"
    )

    print(
        "--------------------"
    )

    print()


    folder = input(
        "Enter folder path: "
    ).strip()


    if not folder:

        print(
            "No folder selected."
        )

        sys_exit = False

    else:

        folder = Path(
            folder
        )


        if not folder.exists():

            print(
                "Folder does not exist."
            )

        else:

            print()
            print(
                "Preview:"
            )
            print()


            results, _ = organize_files(
                folder,
                dry_run=True
            )


            for result in results:

                print(
                    result
                )

                print()


            print(
                "Preview finished."
            )