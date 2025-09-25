import json
import logging
import os
from datetime import datetime

from flask import jsonify, request


def load_program_from_file(logger: logging.Logger, program_name: str) -> jsonify:
    # return jsonify({"success": False, "error": "Program not found"}), 404
    try:
        programs_dir = os.path.join(os.getcwd(), "programs")
        program_folder = os.path.join(programs_dir, program_name)

        if not os.path.exists(program_folder):
            return jsonify({"success": False, "error": "Program not found"}), 404

        cpp_file_path = os.path.join(program_folder, "src/main.cpp")
        print("cpp path", cpp_file_path)
        metadata_file_path = os.path.join(program_folder, "metadata.json")

        if not os.path.exists(cpp_file_path):
            return jsonify({"success": False, "error": "Program file not found"}), 404

        # Load code
        with open(cpp_file_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Load metadata if it exists
        metadata = {}
        if os.path.exists(metadata_file_path):
            with open(metadata_file_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

        return jsonify(
            {
                "success": True,
                "program_name": program_name,
                "code": code,
                "metadata": metadata,
            }
        )

    except Exception as e:
        logger.error(f"Error loading program: {str(e)}")
        return (
            jsonify({"success": False, "error": f"Failed to load program: {str(e)}"}),
            500,
        )


def save_program_to_file(logger: logging.Logger) -> jsonify:
    """Save C++ program to file system"""
    try:
        data = request.get_json()
        program_name = data.get("program_name", "").strip()
        code = data.get("code", "")

        if not program_name:
            return jsonify({"success": False, "error": "Program name is required"}), 400

        if not code.strip():
            return jsonify({"success": False, "error": "Code cannot be empty"}), 400

        # Create programs directory if it doesn't exist
        programs_dir = os.path.join(os.getcwd(), "programs")
        if not os.path.exists(programs_dir):
            os.makedirs(programs_dir)

        # Create program-specific folder
        program_folder = os.path.join(programs_dir, program_name)
        if not os.path.exists(program_folder):
            os.makedirs(program_folder)

        # Save main.cpp file
        cpp_file_path = os.path.join(program_folder, "main.cpp")
        with open(cpp_file_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Create metadata file
        metadata = {
            "program_name": program_name,
            "created_at": datetime.now().isoformat(),
            "file_path": cpp_file_path,
            "description": data.get("description", ""),
        }

        metadata_file_path = os.path.join(program_folder, "metadata.json")
        with open(metadata_file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Program '{program_name}' saved successfully to {program_folder}")

        return jsonify(
            {
                "success": True,
                "message": f'Program "{program_name}" saved successfully',
                "file_path": cpp_file_path,
                "folder_path": program_folder,
            }
        )

    except Exception as e:
        logger.error(f"Error saving program: {str(e)}")
        return (
            jsonify({"success": False, "error": f"Failed to save program: {str(e)}"}),
            500,
        )


def list_all_programs(logger: logging.Logger) -> jsonify:
    """List all saved programs"""
    try:
        programs_dir = os.path.join(os.getcwd(), "programs")

        if not os.path.exists(programs_dir):
            return jsonify({"success": True, "programs": []})

        programs = []
        for folder_name in os.listdir(programs_dir):
            folder_path = os.path.join(programs_dir, folder_name)
            if os.path.isdir(folder_path):
                cpp_file_path = os.path.join(folder_path, "src/main.cpp")
                metadata_file_path = os.path.join(folder_path, "metadata.json")

                if os.path.exists(cpp_file_path):
                    program_info = {"name": folder_name, "folder_path": folder_path}

                    # Load metadata if available
                    if os.path.exists(metadata_file_path):
                        try:
                            with open(metadata_file_path, "r", encoding="utf-8") as f:
                                metadata = json.load(f)
                                program_info.update(metadata)
                        except:
                            pass

                    programs.append(program_info)

        return jsonify({"success": True, "programs": programs})

    except Exception as e:
        logger.error(f"Error listing programs: {str(e)}")
        return (
            jsonify({"success": False, "error": f"Failed to list programs: {str(e)}"}),
            500,
        )
