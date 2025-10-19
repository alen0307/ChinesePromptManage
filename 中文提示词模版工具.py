import json
import random
from pathlib import Path

CONFIG_FILE = "中文提示词模板.json"

class ChinesePrompts:
	@classmethod
	def INPUT_TYPES(cls):
		cfg = cls._load_cfg() or {}
		# 给每个列表字段加“⸺”作为首项
		menus = {k: (["⸺"] + v,) for k, v in cfg.items()
				 if isinstance(v, list) and v and isinstance(v[0], str)}
		return {
			"required": {
				"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
				**menus,
			}
		}

	RETURN_TYPES = ("STRING",)
	FUNCTION = "generate"
	CATEGORY = "爱老天荒"

	@staticmethod
	def _load_cfg():
		try:
			p = Path(__file__).parent / CONFIG_FILE
			with p.open("r", encoding="utf-8") as f:
				return json.load(f)
		except Exception:
			return None

	def generate(self, seed, **kwargs):
		cfg = self._load_cfg()
		if cfg is None:
			return ("❌ 无法读取配置文件",)

		random.seed(seed)
		selected = {}

		# 逐字段处理
		for key, lst in cfg.items():
			if not (isinstance(lst, list) and lst and isinstance(lst[0], str)):
				continue
			user_pick = kwargs.get(key, "⸺")
			if user_pick == "⸺":
				selected[key] = random.choice(lst)
			else:
				selected[key] = user_pick

	   # 2. 拆分“场景” -> “场景”+“场景细节”  （必须先做）
		if "场景" in selected:
			place, place_desc = selected["场景"].split("｜", 1) if "｜" in selected["场景"] else (selected["场景"], "")
			selected["场景"] = place
			selected["场景细节"] = place_desc	   # 保证字典里有这个 key
		# 二级模板递归渲染
		for k in list(selected):
			if isinstance(selected[k], str):
				for _ in range(3):
					try:
						new_val = selected[k].format(**selected)
						if new_val == selected[k]:
							break
						selected[k] = new_val
					except (KeyError, ValueError):
						break

		prompt = selected["中文模版"].format(**selected)
		return (prompt,)

NODE_CLASS_MAPPINGS = {"ChinesePrompts": ChinesePrompts}
NODE_DISPLAY_NAME_MAPPINGS = {"ChinesePrompts": "🧓 中文提示词模版"}