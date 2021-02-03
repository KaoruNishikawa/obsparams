"""Obtain codes from GitHub, and analyse it.

This module is a collection of tools to list parameters or certain
expressions used/declared in .py, .launch, and .obs codes.

"""

from github import Github
import xml.etree.ElementTree as ET
import importlib.util
import base64
import re


class obsfile_params_check(object):

    def __init__(self, token):
        self.g = Github(token)

    def list_repos(self, username):
        """Get list of repository names.

        Parameters
        ----------
        username : str
            Github username, with no whitespace, case insensitive.

        Return
        ------
        list
            List of repository names.

        Examples
        --------
        >>> obsfile_params_check().list_repos("kaorunishikawa")
        ['ros1_test', 'ros2_test']

        """
        repos = self.g.get_user(username).get_repos(type="owner")
        return [repo.name for repo in repos]

    def list_files(self, path):
        """Get list of files in specified repository or directory.

        Parameters
        ----------
        path : str
            Github repository name or its directory path, with no
            whitespace, case insensitive.

        Return
        ------
        list
            List of file names. All files in child directories are
            included, but directory paths are NOT included.

        Examples
        --------
        >>> check = obsfile_params_check()
        >>> check.list_files("kaorunishikawa/ros1_test/shellscript/tools")
        ['shellscript/tools/launch_flex_generator.sh', 'shellscript/tools/launch_generator.sh']

        """  # noqa: E501
        path = path.split("/", 2)
        try:
            user, repository, directory = path[0], path[1], path[2]
        except IndexError:
            try:
                user, repository, directory = path[0], path[1], ""
            except IndexError:
                raise IndexError(
                    "'username/repository' must be included in the path."
                )
        repo = self.g.get_repo(f"{user}/" + repository)
        contents = repo.get_contents(directory)
        if not isinstance(contents, list):
            contents = [contents]
        self.__content = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                self.__content.append(file_content)
        return [content.path for content in self.__content]

    def get_file_dict(self, path):
        self.list_files(path)
        return [
            {content.path.split("/")[-1]: content.path}
            for content in self.__content
        ]

    def read_file(self, path):
        """Get contents of the file.

        Parameters
        ----------
        path : str
            Github path to the file, starting with repositpry name.

        Return
        ------
        bytes
            What's written in the file.

        Examples
        --------
        >>> check = obsfile_params_check()
        >>> check.read_file("kaorunishikawa/ros1_test/README.md")
        '# ros1_test'
        >>> check.read_file("kaorunishikawa/ros1_test/shellscript")
        Traceback (most recent call last):
            ...
        ValueError: File is not uniquely specified.

        """
        self.list_files(path)
        file_content = self.__content
        if len(file_content) > 1:
            raise ValueError("File is not uniquely specified.")
        return base64.b64decode(file_content[0].content).decode()

    def get_obsparams(self, path):
        """List parameters declared in obsfile.

        Parameters
        ----------
        path : str
            Github path to the obsfile, starting with repositpry name.

        Return
        ------
        list
            Parameters declared in the file.

        Examples
        --------
        >>> check = obsfile_params_check()
        >>> check.get_obsparams("nanten2/necst-obsfiles/horizon.obs")
        ['offset_Az', 'offset_El', 'lambda_on', 'beta_on', 'lambda_off', 'beta_off', 'coordsys', 'object', 'vlsr', 'tuning_vlsr', 'cosydel', 'otadel', 'start_pos_x', 'start_pos_y', 'scan_direction', 'exposure', 'otfvel', 'otflen', 'grid', 'N', 'lamdel_off', 'betdel_off', 'otadel_off', 'nTest', 'datanum', 'lamp_pixels', 'exposure_off', 'observer', 'obsmode', 'purpose', 'tsys', 'acc', 'load_interval', 'cold_flag', 'pllref_if', 'multiple', 'pllharmonic', 'pllsideband', 'pllreffreq', 'restfreq_1', 'obsfreq_1', 'molecule_1', 'transiti_1', 'lo1st_sb_1', 'if1st_freq_1', 'lo2nd_sb_1', 'lo3rd_sb_1', 'lo3rd_freq_1', 'if3rd_freq_1', 'start_ch_1', 'end_ch_1', 'restfreq_2', 'obsfreq_2', 'molecule_2', 'transiti_2', 'lo1st_sb_2', 'if1st_freq_2', 'lo2nd_sb_2', 'lo3rd_sb_2', 'lo3rd_freq_2', 'if3rd_freq_2', 'start_ch_2', 'end_ch_2', 'fpga_integtime']

        """  # noqa: E501
        content = self.read_file(path)
        lines = content.splitlines()
        param_val = [line.split("=") for line in lines]
        params = []
        for param_val_ in param_val:
            try:
                if param_val_[1]:
                    params.append(param_val_[0])
            except IndexError:
                pass  # to ignore last line
        return params

    def params_extract(self, trigger, path, already_escaped=False):
        """List parameters referenced in the file.

        Parameters
        ----------
        trigger : list of str
            Prefix and surfix to the param reference, such as dictionary
            expression.
        path : str
            Github path to the obsfile, starting with repositpry name.
        already_escaped : bool
            Whether the trigger parameters are given with consideration
            of escape sequence or not.

        Return
        ------
        list
            Parameters used in the file.

        Notes
        -----
        trigger example : if the code references params as "obsfile['param']",
        trigger=['obsfile[', ']']

        Examples
        --------
        >>> check = obsfile_params_check()
        >>> check.params_extract(["obs[", "]"], "nanten2/necst-ros/obs_scripts/otf_xffts4.py")
        ['N', 'beta_off', 'beta_on', 'betdel', 'betdel_off', 'coordsys', 'cosydel', 'exposure', 'exposure_off', 'grid', 'lambda_off', 'lambda_on', 'lamdel', 'lamdel_off', 'lamp_pixels', 'lo1st_sb_1', 'lo1st_sb_2', 'load_interval', 'molecule_1', 'nTest', 'object', 'obsmode', 'otadel', 'otadel_off', 'otflen', 'otfvel', 'restfreq_1', 'scan_direction', 'start_pos_x', 'start_pos_y', 'transiti_1', 'vlsr']

        """  # noqa: E501
        content = self.read_file(path)
        if not already_escaped:
            trigger = [re.escape(trig) for trig in trigger]
        params = re.findall(
            f"{trigger[0]}['\"](.*?)['\"].*?{trigger[1]}", content
        )
        params = list(set(params))
        return sorted(params)

    def params_extract_match(self, trigger, path, already_escaped=False):
        content = self.read_file(path)
        if not already_escaped:
            trigger = [re.escape(trig) for trig in trigger]
        params = re.findall(
            f"{trigger[0]}['\"](.*?)['\"].*?{trigger[1]}", content
        )
        if not isinstance(params, list):
            params = [params]
        all_params = re.findall(
            f"{trigger[0]}(.*?).*?{trigger[1]}", content
        )
        true_params = []
        for param in all_params:
            if param not in params:
                param_ = re.findall(
                    f"{param} = ['\"](.*?)['\"]", content
                )
                try:
                    true_params.append(param_[0])
                except IndexError:
                    print("couldn't parse" + path)
        params = list(set(params + true_params))
        # params = list(params)
        return sorted(params)
        # return (params, true_params)

    def params_extract_eval(
        self, trigger, path, already_escaped=False, ignore_import=False
    ):
        """List certain expressions in the file.

        Parameters
        ----------
        trigger : list of str
            Prefix and surfix to the param reference, such as dictionary
            expression.
        path : str
            Github path to the obsfile, starting with repositpry name.
        already_escaped : bool
            Whether the trigger parameters are given with consideration
            of escape sequence or not.
        ignore_import : bool
            Whether to ignore (from)import lines, to avoid mis-detection
            caused by import errors.

        Return
        ------
        list
            Parameters used in the file.

        Notes
        -----
        trigger example : if the code references params as "obsfile['param']",
        trigger=['obsfile[', ']']

        Examples
        --------
        >>> check = obsfile_params_check()
        >>> check.params_extract(["obs[", "]"], "nanten2/necst-ros/obs_scripts/otf_xffts4.py")
        ['N', 'beta_off', 'beta_on', 'betdel', 'betdel_off', 'coordsys', 'cosydel', 'exposure', 'exposure_off', 'grid', 'lambda_off', 'lambda_on', 'lamdel', 'lamdel_off', 'lamp_pixels', 'lo1st_sb_1', 'lo1st_sb_2', 'load_interval', 'molecule_1', 'nTest', 'object', 'obsmode', 'otadel', 'otadel_off', 'otflen', 'otfvel', 'restfreq_1', 'scan_direction', 'start_pos_x', 'start_pos_y', 'transiti_1', 'vlsr']

        """  # noqa: E501
        content = self.read_file(path)
        if not already_escaped:
            trigger = [re.escape(trig) for trig in trigger]
        params = re.findall(
            f"{trigger[0]}['\"](.*?)['\"]{trigger[1]}", content
        )
        all_params = re.findall(f"{trigger[0]}(.*?){trigger[1]}", content)
        if ignore_import:
            content = re.sub(r".*?import.*?\n", r"\n", content)
            content = re.sub(r"sys.path.*?\n", r"\n", content)
            content = re.sub(r"if.*?\n", r"\n", content)
            content = re.sub(r"for.*?\n", r"\n", content)
            content = re.sub(r"while.*?\n", r"\n", content)
            content = re.sub(r" {4}", r"", content)
        true_params = []
        for param in all_params:
            if param not in params:
                true_params.append(self.eval_param(path, content, param))
        params = list(set(params + true_params))
        return sorted(params)

    @staticmethod
    def eval_param(path, content, param):
        """List certain expressions in the file.

        Parameters
        ----------
        path : str
            Github path to the obsfile.
        content : str
            Content of the file.
        param : str
            String sequence to evaluate and extract.

        Return
        ------
        str
            Parameter evaluated.

        Notes
        -----
        This is staticmethod, so no need to instantiate the class to use
        this. Some output will show up while executing the content, but
        this method RETURNs evaluated parameter only.
        By restriction of making this document, 'content' is given in
        escaped format. It will cause an error when running this method,
        so input 'content' without escaping any letter.

        Examples
        --------
        >>> check = obsfile_params_check()
        >>> check.eval_param("ros1_test/dummy_node.py", "#!/usr/bin/env python3\\n\\nnode_name = 'dummy'\\nlen(node_name)", "node_name")
        'node_name -> dummy'
        >>> obsfile_params_check.eval_param("ros1_test/dummy_node.py", "#!/usr/bin/env python3\\n\\nnode_name = 'dummy'\\nlen(node_name)", "node_name")
        'node_name -> dummy'

        """  # noqa: E501
        filename = re.split("/", path)[-1]
        m = re.search(r"\.", filename)
        filename = filename[: m.start()]  # remove extension (e.g. '.py')
        if not isinstance(param, str):
            param = str(param)
        # build module
        spec = importlib.util.spec_from_loader(filename, loader=None)
        pymodule = importlib.util.module_from_spec(spec)
        try:
            exec(content, pymodule.__dict__)
        except ModuleNotFoundError as e:
            print(e, f"\nIncompletely imported {filename}.")
        except NameError as e:
            print(e, f"\nIncompletely imported {filename}.")
        except IndentationError as e:
            print(e, f"\nIncompletely imported {filename}.")
        try:
            true_param = eval(f"pymodule.{param}")
        except Exception as e:
            true_param = "???"
            print(e)
            print("Reference cannot be resolved.")
        print(true_param)
        return param + " -> " + str(true_param)

    def list_from_launch(self, path, path_dict):
        """List all nodes launched by the launch file.

        All nodes including same node with different name, which are
        launched by the launch file are listed.

        Parameters
        ----------
        path : str
            Github path to the launch file.
        path_dict : dict
            Dictionary that relates file name to its full path,
            generated by `obsfile_params_check().get_file_dict(path)`

        Return
        ------
        list of dict
            List of dictionary which contains node filename and remap
            rules.
        """
        if path[-7:] != ".launch":
            return []
        code = self.read_file(path)
        path = path.split("/", 2)
        user, repository, file_path = path[0], path[1], path[2]  # noqa: F841
        root = ET.fromstring(code)
        elements = [elem for elem in root]
        nodes = []
        while elements:
            child = elements.pop(0)
            if child.tag == "include":
                launch_path = child.get("file").split("/", 1)[1]
                launch_path = "/".join([user, repository, launch_path])
                code = self.read_file(launch_path)
                elements.extend(ET.fromstring(code))
            else:
                nodes.append(child)
        ret = []
        for node in nodes:
            ret.append(
                {
                    "type": node.get("type"),
                    "remap": [
                        {remap.get("from"): remap.get("to")}
                        for remap in node.iter("remap")
                    ],
                }
            )
        return ret

    def extract_mapping(self, path):
        code = self.read_file(path)
        code = re.sub(" *?", "", code)
        code = re.sub("={3,}", "", code)
        code = code.split("\n")
        code = [re.sub("^.*?:", "", line) for line in code]
        code = [line.split("=", 1) for line in code]
        mapping = []
        for line in code:
            try:
                if line[1]:
                    mapping.append({line[0]: line[1]})
            except IndexError:
                pass
        return mapping

    def diff(self, params_declared, params_used):
        """Compare parameters declared and used.

        Parameters
        ----------
        params_declared : list of str
            Parameters declared in obsfile.
        params_used : list of str
            Parameters used in the file.

        Return
        ------
        dict of list
            'used' for parameters declared and used, 'not_used' for
            parameters declared but not used, and 'not_declared' for
            parameters not declared.

        Examples
        --------
        >>> check = obsfile_params_check()
        >>> used = check.params_extract(["obs[", "]"], "nanten2/necst-ros/obs_scripts/otf_xffts4.py")
        >>> declared = check.get_obsparams("nanten2/necst-obsfiles/horizon.obs")
        >>> check.diff(declared, used)
        {'used': ['lambda_on', 'beta_on', 'lambda_off', 'beta_off', 'coordsys', 'object', 'vlsr', 'cosydel', 'otadel', 'start_pos_x', 'start_pos_y', 'scan_direction', 'exposure', 'otfvel', 'otflen', 'grid', 'N', 'lamdel_off', 'betdel_off', 'otadel_off', 'nTest', 'lamp_pixels', 'exposure_off', 'obsmode', 'load_interval', 'restfreq_1', 'molecule_1', 'transiti_1', 'lo1st_sb_1', 'lo1st_sb_2'], 'not_used': ['offset_Az', 'offset_El', 'tuning_vlsr', 'datanum', 'observer', 'purpose', 'tsys', 'acc', 'cold_flag', 'pllref_if', 'multiple', 'pllharmonic', 'pllsideband', 'pllreffreq', 'obsfreq_1', 'if1st_freq_1', 'lo2nd_sb_1', 'lo3rd_sb_1', 'lo3rd_freq_1', 'if3rd_freq_1', 'start_ch_1', 'end_ch_1', 'restfreq_2', 'obsfreq_2', 'molecule_2', 'transiti_2', 'if1st_freq_2', 'lo2nd_sb_2', 'lo3rd_sb_2', 'lo3rd_freq_2', 'if3rd_freq_2', 'start_ch_2', 'end_ch_2', 'fpga_integtime'], 'not_declared': ['betdel', 'lamdel']}

        """  # noqa: E501
        used, not_used, not_declared = [], [], []
        for param in params_declared:
            if param in params_used:
                used.append(param)
            else:
                not_used.append(param)
        for param in params_used:
            if param not in params_declared:
                not_declared.append(param)
        ret = {
            "used": used, "not_used": not_used, "not_declared": not_declared
        }
        return ret


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
