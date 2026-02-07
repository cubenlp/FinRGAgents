#encoding:utf-8
import abc
from textwrap import dedent
from fin2rg.utils import query_llm
import re

class PromptBuild(abc.ABC):
    def build(self):
        # 获取类中的所有实例变量
        instance_vars = {k: v for k, v in vars(self).items()}
        # 使用这些变量来格式化类的 docstring
        return dedent(self.__class__.__doc__).format_map(instance_vars)
    
    def predict(self,model):
        prompt_tmp = self.build()
        return query_llm(prompt_tmp,model=model)




# figure 10.The prompt for planning a draft of major
class MajorClaimDraftGenPrompt(PromptBuild):
    """
    Writing prompt: {input}
    Write a concise, contentious, and coherent Thesis Statement (major claim)
    given the writing prompt.
    """
    
    def __init__(self, input):
        self.input = input


# Figure 11: The prompt for planning draft of claims.        
class BranchClaimsDraftGenPrompt(PromptBuild):
    """
    Major Claim: {input}
    To support the major claim, please further derive {num_branches} effective
    claims in one sentence. Think about the claims from different perspectives.
    Please Note that each claim must end with token <sep>.
    """
    def __init__(self,input,num_branches):
        self.input = input
        self.num_branches = num_branches

    @staticmethod
    def parse_branch_list(branches_list_str):

        import re
        # 原始字符串
        text = branches_list_str

        # """1. 宁德时代在动力电池和储能电池领域的全球市场份额持续增长，显示出其强大的市场竞争力<sep>.
        # 2. 宁德时代通过持续的技术创新，如高能量密度电池和快速充电技术，提升了产品性能和市场吸引力<sep>.
        # 3. 宁德时代积极布局全球市场，特别是在欧洲和北美的新能源汽车市场，扩大了其国际影响力<sep>.
        # 4. 宁德时代通过垂直整合供应链和优化生产流程，有效控制了成本，增强了盈利能力<sep>.
        # 5. 宁德时代与多家全球知名汽车制造商建立了战略合作关系，确保了稳定的订单和市场份额<sep>.
        # 6. 宁德时代在应对原材料价格波动方面采取了多元化采购策略和期货对冲手段，降低了风险<sep>."""


        # 使用<sep>分割字符串
        items = text.split('<sep>')
        if len(items[-1]) < 2:
            items = items[:-1]

        # 使用正则表达式去除每个元素前的序号
        pattern = re.compile(r'^[\\.\n]*\d+\.\s*')  # 匹配形如 "1. " 的序号
        cleaned_items = [pattern.sub('', item).strip() for item in items]
        
        
        return cleaned_items

        


# Figure 12: The prompt for planning the overriding and undercutting rebuttals.
class ClaimRebuttalsGenPrompt(PromptBuild):
    """
    Claim: {claim}
    Evaluate the claim and refute it. Only output {num_branches} pieces of
    rebuttal. Please Note that each rebuttal must end with a special token <sep>.
    """
    def __init__(self,claim, num_branches):
        self.claim = claim
        self.num_branches = num_branches

class ClaimRebuttalsGenWithInputPrompt(PromptBuild):
    """
    Writing prompt: {input}
    Claim: {claim}
    Evaluate the claim and refute it. Only output {num_branches} pieces of
    rebuttal. Please Note that each rebuttal must end with a special token <sep>.
    """
    def __init__(self,input,claim, num_branches):
        self.input = input
        self.claim = claim
        self.num_branches = num_branches

        
# Figure 13: The prompt for planning refined claims.
class ClaimRefinePrompt(PromptBuild):
    """
    Claim: {claim}
    Rebuttal: {rebuttal}
    Improve the above claim considering the weakness that the rebuttal points
    out. Directly output an improved claim in one sentence without any sup-
    porting evidence or acknowledging the weakness again.
    """
    def __init__(self,claim,rebuttal):
        self.claim = claim
        self.rebuttal = rebuttal

# Figure 13: The prompt for planning refined claims.
class ClaimRefineWithInputPrompt(PromptBuild):
    """
    Writing prompt: {input}
    Claim: {claim}
    Rebuttal: {rebuttal}
    Improve the above claim considering the weakness that the rebuttal points
    out. Directly output an improved claim in one sentence without any sup-
    porting evidence or acknowledging the weakness again.
    """
    def __init__(self,input,claim,rebuttal):
        self.input = input
        self.claim = claim
        self.rebuttal = rebuttal


# Figure 14: The prompt for planning counter-rebuttals.
class CounterRebuttalGenPrompt(PromptBuild):
    """
    Claim: {claim}
    Rebuttal: {rebuttal}
    Carefully review the claim and rebuttal. Please write a brief and persuasive
    counter-rebuttal to defend your claim or give solutions. Only output the
    counter-rebuttal.
    """
    def __init__(self,claim,rebuttal):
        self.claim = claim
        self.rebuttal = rebuttal


# Figure 15: The prompt for planning the final major
class MajorClaimGenPrompt(PromptBuild):
    """
    Writing prompt: {input}
    Claims: {claims}
    Please provide a concise, powerful Thesis statement (major claim) 
    no longer than 20 words that encompasses the primary points of the provided claims.
    """
    def __init__(self,input,claims):
        self.claims = claims
        self.input = input


# Figure: The prompt for generating a stock research report outline.
class StockResearchOutlinePrompt(PromptBuild):
    # """
    # Key Research Focus: {main_argument}
    # Supporting Points: {sub_arguments}
    # Generate a detailed stock research report outline focusing on the key research focus and supporting points.
    # Use '#' for section titles and '##' for subsection titles. 
    # Only output section headings without providing supporting analysis or details.
    # Generate no more than 2 secondary chapter titles.
    # """
    """
    Main Argument: {main_argument}
    Sub arguments: {sub_arguments}
    Main Argument as the title and sub arguments as the secondary title. For the sub-arguments, generate detailed tertiary headings that clearly state the viewpoints.
    Use '#' for section titles and '##' for subsection titles. 
    Only output section headings without providing supporting analysis or details.
    Generate no more than 2 tertiary chapter titles.
    The output format is JSON format: 'title': 'title content', '1. first level chapter name': ['1.1 second level chapter name', '1.2 second level chapter name', ...]
    """
    def __init__(self, main_argument, sub_arguments):
        self.main_argument = main_argument
        self.sub_arguments = sub_arguments



# Figure: The prompt for generating a research report outline.
class ResearchReportOutlinePrompt(PromptBuild):
    """
    Main Argument: {main_argument}
    Sub-arguments: {sub_arguments}
    Generate a detailed research report outline based on the main argument and sub-arguments.
    Use '#' for section titles and '##' for subsection titles. 
    Only output section headings without supporting details.
    """
    def __init__(self, main_argument, sub_arguments):
        self.main_argument = main_argument
        self.sub_arguments = sub_arguments
