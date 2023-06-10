//Input:
//txt = forxxorfxdofr
//pat = for
//Output: 3
#include<iostream>
#include<bits/stdc++.h>
#include<string>
using namespace std;
  
 /*void solve(string s, string ana) 
 {
   
    return;

}*/

int main()
{
    string s;
    cin>> s;
    string ana;
    cin>> ana;

    //solve(s, ana);
    //cout<< solve;
     int j =0,i =0;
    int ans = 0;
    int N = s.length();
    int K = ana.length();

    unordered_map<char, int> m; //unordered set or map anyone gives O(1)(average) time complexity
     for (int x = 0; x < ana.size(); x++) // in worst case is linear in nature,O(set size)
        {
            m[ana[x]]++;
        }
    
    int count = m.size();
    //cout<<m.size()<<"   ";

    while (j < N) 
    {

        if (m.find(s[j]) != m.end()) 
        {   
            m[s[j]]--;

            if(m[s[j]] == 0) {
                count--;   
            }
        }
       

        if(j-i+1 < K) {
            j++;
        }

       

       else if (j-i+1 == K) 
        {
            
            if( count == 0) {
                ans++;
            }
                                                
            if(m.find(s[i])!=m.end()){ 
                m[s[i]]++;
             
                if(m[s[i]]==1) {
                    count++;    
                }   
            }
            i++;
            j++;                    

        }   
            //if(m[s[i]] >=0 ) {  // before sliding the window we have to increase the i'th value in MAP

         
    }
    cout << ans;
    
}

/* #include<bits/stdc++.h>

using namespace std;

int  solve(string s1,string s2) {
    unordered_map<char ,int > m;
    for(int i=0;i<s2.length();i++) {
        m[s2[i]]++;
    }

    int count = m.size();

    int i=0;
    int j=0;
    int ans =0;
    int n = s1.length();
    int k = s2.length();

    while(j<n) {
        
        if(m.find(s1[j]) != m.end()) {
            m[s1[j]]--;
            if( m[s1[j]] == 0) count--;
        }

        if( j-i+1 < k) {
            j++;
        }

        else if( j-i+1 == k) {

            if ( count == 0) {
                ans++;
            }
            if(m.find(s1[i]) != m.end()) {
                m[s1[i]]++;
                if(m[s1[i]] >0 ) count++;
            }
            i++;
            j++;
        }
    }

    return ans;
}

int main()
{
    string s1;
    cin>>s1;
    string s2;
    cin>>s2;
    cout<<solve(s1,s2);
}*/